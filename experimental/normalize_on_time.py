
#   Author - Vamshi Chenna
#   Normalize on time takes 6 minutes on a Ubunutu Operating Systems with 16G RAM.

import json
import shutil
import glob
import os

import pyspark
from pyspark import SparkContext, SparkConf
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.functions import col, collect_list, concat_ws, udf
from pyspark.sql.functions import struct
from pyspark.sql.types import DoubleType
from pyspark.sql.types import StringType
from dateutil.relativedelta import relativedelta
from datetime import datetime
import pandas as pd
import numpy as np
import re
import ast

from operator import itemgetter

conf = SparkConf().setAppName('yelp-dataset-challenge').setMaster('local[*]')
sc = SparkContext(conf=conf)
spark = SparkSession(sc)

def process_json(data):
    data = json.loads(data)
    return data['business_id'], data['user_id'], data['stars'], data['date']

# Load JSON into pyspark DataFrame.
data = (sc.textFile('yelp_dataset/yelp_academic_dataset_review.json')
          .map(process_json)
          .toDF(['business_id', 'user_id', 'stars', 'date']))
pattern = re.compile(r'Restaurant|Alcohol')


def is_valid_attr(dct):
    return any(pattern.match(k) for k in dct.keys())



def normalizeUserRatings(data_list):
    stars = []
    dates =  []
    for val in data_list:
        stars.append(val.stars)
        dates.append(datetime.strptime(val.date, '%Y-%m-%d'))
    maxDate = max(dates)
    ratios = []
    for e in dates:
        diff =  relativedelta(maxDate,e).years
        ra = 0
        if(diff<10):
            ra = (10-diff)/10.0
        ratios.append(ra)
    mult = 0
    index = 0
    for st in stars:
        mult = st*ratios[index] + mult
        index = index + 1
    sol = " ".join(str(x) for x in ratios)
    return mult/sum(ratios)

userUDF = udf(normalizeUserRatings, DoubleType())

def normalizeBusinessRatings(data_list):
    stars = []
    dates = []
    for val in data_list:
        stars.append(val.sstars_normalized)
        dates.append(datetime.strptime(val.date, '%Y-%m-%d'))
    maxDate = max(dates)
    ratios = []
    for e in dates:
        diff =  relativedelta(maxDate, e).years
        ra = 0
        if(diff<10):
            ra = (10-diff)/10.0
        ratios.append(ra)
    mult = 0
    index = 0
    for st in stars:
        mult = st*ratios[index] + mult
        index = index + 1
    sol = " ".join(str(x) for x in ratios)
    return mult/sum(ratios)


businessUDF = udf(normalizeBusinessRatings, DoubleType())

(data
    .withColumn('starsanddate', struct(col('stars'), col('date')))
    .groupBy(F.col('user_id').alias('user_id#2')).agg(collect_list('starsanddate').alias("starsandData"))
    .withColumn('user_norm_stars', userUDF('starsandData'))
    .join(data, F.col('user_id') == F.col('user_id#2'), 'inner')
    # Mean-shift stars by mean user rating.
    .withColumn('sstars_normalized', F.col('stars') - F.col('user_norm_stars'))
    # Drop unneeded columns.
    .drop('user_id#2', 'user_norm_stars', 'stars')
    # Group on business_id.
    .withColumn('busstarsanddate', struct(col('sstars_normalized'), col('date')))
    .groupby(F.col('business_id')).agg(collect_list('busstarsanddate').alias("busstarsandDate"))
    # Find the mean business rating.
    .withColumn('buss_norm_stars', businessUDF('busstarsandDate'))
    .drop('busstarsanddate')
    .repartition(1)
    .write
    .mode('overwrite')
    .format("csv")
    .option("header", "false")
    .save('yelp_dataset/review_normalized'))

shutil.move(next(glob.iglob('yelp_dataset/review_normalized/part-00000-*.csv')),
            'yelp_dataset/review_normalized.csv')
shutil.rmtree('yelp_dataset/review_normalized/')
shutil.rmtree('spark-warehouse/')

business_json_df = (pd.read_json('yelp_dataset/yelp_academic_dataset_business.json', lines=True)
                      .set_index('business_id')
                      .dropna(subset=['attributes']))
mask = (business_json_df['attributes'].map(is_valid_attr)
        | business_json_df['categories'].str.contains(r"Food|Restaurant|Bar", case=False)
        | business_json_df['name'].str.contains("Restaurant|Cuisine", case=False))
business_json_df = business_json_df[mask]

review_df = (pd.read_csv('yelp_dataset/review_normalized.csv', header=None, names=['business_id', 'rating'])
                .set_index('business_id'))

elevation_df = (pd.read_csv("yelp_dataset/altitude.csv", usecols=['business_id', 'elevation'])
                 .set_index('business_id'))

attributes = business_json_df.pop('attributes')

attr_df = pd.DataFrame(attributes.tolist(), index=attributes.index)

cat_cols = ['Alcohol', 'NoiseLevel', 'RestaurantsAttire', 'RestaurantsPriceRange2', 'WiFi']
cat_df = (pd.concat([attr_df[c].str.get_dummies() for c in cat_cols], axis=1)
            .rename({'casual': 'casual_attire'}, axis=1)
            # Assign meaningful column name for price range.
            .rename(lambda x: '$' * int(x) if x.isdigit() else x, axis=1))
# Handle attributes with boolean values.
bool_cols = ['BikeParking', 'BusinessAcceptsCreditCards', 'Caters', 'GoodForKids',
             'HasTV', 'OutdoorSeating', 'RestaurantsDelivery', 'RestaurantsGoodForGroups',
             'RestaurantsReservations', 'RestaurantsTableService', 'RestaurantsTakeOut',
             'WheelchairAccessible']
bool_df = attr_df[bool_cols].fillna('False').applymap({'True': 1, 'False': 0}.get)

mult_cols = ['Ambience', 'BusinessParking', 'GoodForMeal']
mult_df = []
for c in mult_cols:
    df = attr_df[c].dropna()
    df = (pd.DataFrame(df.apply(ast.literal_eval).tolist(),
                       index=df.index)
            .reindex(attr_df.index)
            .fillna(False)
            .astype(int))

    mult_df.append(
            df
        )
mult_df = pd.concat(mult_df, axis=1)

business_json_df = (
    business_json_df[['categories']]
        .join(elevation_df)
        .join(review_df)
        .join(cat_df)
        .join(bool_df)
        .join(mult_df)
        .sort_index(axis=1))

print(business_json_df.head(10))
print(business_json_df.shape)
print(business_json_df.columns)

msk = np.random.rand(len(business_json_df)) <= 0.8
train = business_json_df[msk]
test = business_json_df[~msk]

train.to_csv('yelp_dataset/businesses_train.csv')
test.to_csv('yelp_dataset/businesses_test.csv')

print('Done.')
