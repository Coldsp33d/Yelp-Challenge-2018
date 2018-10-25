"""PySpark-based rating normalization script.

@author Shiva Deviah
"""
import json
import shutil
import glob
import os

import pyspark
from pyspark import SparkContext, SparkConf
from pyspark.sql import SparkSession
from pyspark.sql import functions as F  
from operator import itemgetter   

conf = SparkConf().setAppName('yelp-dataset-challenge').setMaster('local[*]')
sc = SparkContext(conf=conf)
spark = SparkSession(sc)

def process_json(data):
    data = json.loads(data)
    return data['business_id'], data['user_id'], data['stars']

# Load JSON into pyspark DataFrame.
data = (sc.textFile('yelp_dataset/yelp_academic_dataset_review.json')
          .map(process_json)
          .toDF(['business_id', 'user_id', 'stars']))

(data
    # Group on user_id.
    .groupBy(F.col('user_id').alias('user_id#2'))  
    # Find the mean.
    .mean('stars')                                 
    .withColumnRenamed('avg(stars)', 'average_stars')
    # Join mean with data. 
    .join(data, F.col('user_id') == F.col('user_id#2'), 'inner')  
    # Mean-shift stars by mean user rating. 
    .withColumn('stars_normalized', F.col('stars') - F.col('average_stars'))  
    # Drop unneeded columns.
    .drop('user_id#2', 'average_stars', 'stars')
    # Group on business_id.   
    .groupby(F.col('business_id'))
    # Find the mean business rating.
    .mean('stars_normalized')
    # Coalesce to single partition and write to disk.
    .coalesce(1)  
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
