# coding: utf-8
from sklearn.preprocessing import (
        StandardScaler, Imputer, MinMaxScaler, LabelEncoder)
from sklearn.cluster import AgglomerativeClustering

from pyspark import SparkContext, SparkConf 
from pyspark.mllib.linalg import Vectors
from pyspark.mllib.linalg.distributed import RowMatrix

from timeit import default_timer as timer

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import re
import os
import ast
import argparse
import sys

pattern = re.compile(r'Restaurant|Alcohol')
def is_valid_attr(dct):
        return any(pattern.match(k) for k in dct.keys())

def freq_encode(ser):
        return ser.map(ser.value_counts(normalize=True))

def str2bool(v):
        if v.lower() in ('yes', 'true', 't', 'y', '1'):
                return True
        elif v.lower() in ('no', 'false', 'f', 'n', '0'):
                return False
        else:
                raise argparse.ArgumentTypeError('Boolean value expected.')

try:
        del os.environ['PYSPARK_SUBMIT_ARGS']
except KeyError:
        pass

parser = argparse.ArgumentParser(description='Flexible Yelp Dataset Preprocessing script.')
parser.add_argument('--withCluster', 
                    required=False,
                    type=str2bool,
                    nargs='?',
                    const=True, 
                    default=False,
                    help='Preprocess data with cuisine/category labels.')

parser.add_argument('--clusterScheme', 
                    required=False, 
                    choices=['regional', 'svd'], # TODO - if needed, "spacy_w2v" can also be made an option.
                    default='svd')

parser.add_argument('--withOtherBusinesses', 
                    required=False,
                    type=str2bool,
                    nargs='?',
                    const=True, 
                    default=False,
                    help='Include extra (non-restaurant businesses) rows for training the model.')

parser.add_argument('--withTrainTestSplit', 
                    required=False,
                    type=str2bool,
                    nargs='?',
                    const=True, 
                    default=False)
args = vars(parser.parse_args())

conf = SparkConf().setAppName("eda").setMaster("local[*]")                                                     
sc = SparkContext(conf=conf)
sc.setCheckpointDir("checkpoint_dir/")

outFile_name = 'businesses'

start = timer()

business_json_df = (pd.read_json('yelp_dataset/yelp_academic_dataset_business.json', lines=True)
                                             # Set the index to business_id; this will be used for joining later.
                                            .set_index('business_id')
                                            .dropna(subset=['attributes', 'categories']))
# Filter out non-restaurant businesses.
mask = (business_json_df['categories'].str.contains(r"Food|Restaurant|Bar", case=False) 
                | business_json_df['name'].str.contains("Restaurant|Cuisine", case=False))

if args['withOtherBusinesses']: 
    outFile_name += '_withOtherBusinesses'
    mask |= business_json_df['attributes'].map(is_valid_attr) 

business_json_df = business_json_df[mask]

attributes = business_json_df.pop('attributes')
attr_df = pd.DataFrame(attributes.tolist(), index=attributes.index)

mult_cols = ['Ambience', 'BusinessParking', 'GoodForMeal']
mult_df = []
for c in mult_cols:
        df = attr_df[c].dropna()
        df = (pd.DataFrame(df.apply(ast.literal_eval).tolist(), 
                                             index=df.index)
                        .rename(lambda x: '{0}_{1}'.format(c, x), axis=1)
                        .reindex(attr_df.index))

        mult_df.append(
                        df
                )
        
mult_df = (pd.concat(mult_df, axis=1)
                         .replace({'True': '1', 'False': '0'})
                         .astype(float))

elevation_df = (pd.read_csv("yelp_dataset/altitude.csv", usecols=['business_id', 'elevation'])
                                 .set_index('business_id'))

review_df = (pd.read_csv('yelp_dataset/review_normalized.csv', header=None, names=['business_id', 'rating'])
                                .set_index('business_id'))

bool_cols = [
     'BikeParking', 'BusinessAcceptsCreditCards', 'Caters', 'GoodForKids', 
         'HasTV', 'OutdoorSeating', 'RestaurantsDelivery', 'RestaurantsGoodForGroups',
         'RestaurantsReservations', 'RestaurantsTableService', 'RestaurantsTakeOut', 
         'WheelchairAccessible'
 ]
bool_df = attr_df[bool_cols].replace({'True': '1', 'False': '0'}).astype(float)

cat_cols = ['Alcohol', 'NoiseLevel', 'RestaurantsAttire', 'RestaurantsPriceRange2', 'WiFi']
business_json_df = (
        business_json_df[['categories']]
                .join(review_df)
                .join(elevation_df)
                # .join(mult_df)
                .join(attr_df[cat_cols])
                .join(bool_df)
                .sort_index(axis=1))

if args['withCluster']:
    print('============Creating Category Column.')
    outFile_name += f'_withCluster<{args["clusterScheme"].title()}>'

    regions = {
        'Spanish', 'Portuguese', 'Latin American', 'African', 'Japanese', 
            'Chinese', 'Indian', 'Pakistani', 'Peruvian', 'French', 'Italian', 
            'Brazillian', 'British', 'German', 'Korean', 'Vietnamese', 'Asian Fusion', 
            'Taiwanese', 'Thai', 'Greek', 'Mediterranean', 'Filipino', 'Persian/Iranian', 
            'Lebanese', 'Turkish', 'American (New)', 'American (Traditional)', 
            'Middle Eastern', 'Caribbean', 'Hawaiian', 'Canadian (New)', 'Irish'
    }

    cats = business_json_df.loc[:, 'categories']
    v = cats.str.split(', ',expand=True).stack()
    cnts = v.value_counts()
    cnts = cnts[cnts.gt(100)]

    cats = cnts.index.dropna()

    if args['clusterScheme'] == 'regional':
        regions_ = list(regions)
        cat_df = pd.Series(pd.factorize(regions_)[0], index=regions_)
        
        v = business_json_df['categories'].map(lambda x: regions.intersection(x.split(', ')))
        label = 'catRegion_label'
    else:
        temp = business_json_df.dropna(subset=['categories'])
        temp = temp[[any(c in x for c in cats) for x in temp['categories']]]

        # Number of data points with just these high level (regional cusine categories) - Roughly 50%
        v = (temp['categories']
                         .str.split(r'\s*,\s*', expand=True)
                         .stack()
                         .reset_index(level=1, drop=True)
                         .to_frame('categories')
                         .assign(rating=temp['rating']))

        cats = (set(pd.read_csv('yelp_dataset/cat100.csv', squeeze=True).unique()) 
                        - regions
                        - {'Food', 'Restaurants'})
        v = v[v['categories'].isin(cats)]

        le = LabelEncoder()
        v['categories'] = le.fit_transform(v['categories'])

        v2 = v.groupby(level=0).apply(lambda g: {x : y for x, y in zip(g['categories'], g['rating'])})

        rdd = sc.parallelize(v2.tolist()).map(lambda x: Vectors.sparse(len(cats), x))
        rdd.cache()
        mat = RowMatrix(rdd)
        svd = mat.computeSVD(len(regions), computeU=True)
        U = svd.U       # The U factor is a RowMatrix.
        s = svd.s       # The singular values are stored in a local dense vector.
        V = svd.V       # The V factor is a local dense matrix.
        vectors = V.toArray()

        cat_df = pd.DataFrame({'category': le.inverse_transform(np.arange(vectors.shape[0]))})
        cluster = AgglomerativeClustering(n_clusters=len(regions), affinity='cosine', linkage='complete')  
        cat_df = cat_df.assign(cat34_label=cluster.fit_predict(vectors)).set_index('category').cat34_label

        v = business_json_df['categories'].map(lambda x: cats.intersection(x.split(', ')))
        label = f'cat{len(cats)}_label'

    v = v[v.str.len().gt(0)]
    # Resolution order for multiple categories is to take the most common (mode) in the dataset.
    v = v.map(lambda x: max(x, key=cnts.get)).map(cat_df).to_frame(label)
    cat_df.to_csv(f'yelp_dataset/catmap_{args["clusterScheme"].title()}.csv')

    business_json_df = business_json_df.join(v)

print('============Exported Data Size:', business_json_df.shape)

if args['withTrainTestSplit']:
    msk = np.random.rand(len(business_json_df)) <= 0.8
    train = business_json_df[msk]
    test = business_json_df[~msk]

    train.to_csv(f'yelp_dataset/{outFile_name}_train.csv')
    test.to_csv(f'yelp_dataset/{outFile_name}_test.csv')
else:
    business_json_df.to_csv(f'yelp_dataset/{outFile_name}.csv')

end = timer()

print(f'Time:', end - start)
