"""PySpark-based rating normalization script."""
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

# Cleaning up.
shutil.move(next(glob.iglob('yelp_dataset/review_normalized/part-00000-*.csv')),
            'yelp_dataset/review_normalized.csv')
shutil.rmtree('yelp_dataset/review_normalized/')
shutil.rmtree('spark-warehouse/')

print('Done Writing.')
