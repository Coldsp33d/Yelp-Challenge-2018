"""Attribute extraction and preprocessing script.

Extract attributes from the "attributes" column, flatten, and join with businesses.
Script takes ~45 seconds to complete on Mac OSX High Sierra (2013 Model) i7.
@author Shiva Deviah
"""
import re
import ast
import os
import sys

import pandas as pd
import numpy as np

# TODO(deviah) - How do we handle categories?

pattern = re.compile(r'Restaurant|Alcohol')
def is_valid_attr(dct):
    return any(pattern.match(k) for k in dct.keys())

try:
    os.stat('yelp_dataset/review_normalized.csv')
except OSError:
    print("Normalized ratings not available. Please run spark-submit normalize.py and try again.")
    sys.exit(-1)

# Load data.
# Load businesses (restaurants) data.
business_json_df = (pd.read_json('yelp_dataset/yelp_academic_dataset_business.json', lines=True)
                       # Set the index to business_id; this will be used for joining later.
                      .set_index('business_id')
                      .dropna(subset=['attributes']))
# Filter out non-restaurant businesses.
mask = (business_json_df['attributes'].map(is_valid_attr) 
        | business_json_df['categories'].str.contains(r"Food|Restaurant|Bar", case=False) 
        | business_json_df['name'].str.contains("Restaurant|Cuisine", case=False))
business_json_df = business_json_df[mask]
# Load normalized reviews data.
review_df = (pd.read_csv('yelp_dataset/review_normalized.csv', header=None, names=['business_id', 'rating'])
                .set_index('business_id'))
# Load altitude data. Altitude information has been extracted using the QGIS tool.
elevation_df = (pd.read_csv("yelp_dataset/altitude.csv", usecols=['business_id', 'elevation'])
                 .set_index('business_id'))
print('Done Loading Data.')

attributes = business_json_df.pop('attributes')
attr_df = pd.DataFrame(attributes.tolist(), index=attributes.index)

# Handle categorical attributes.
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
# Handle attributes with dictionaries of sub-categories.
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
print('Done Processing Attributes.')


business_json_df = (
    business_json_df[['categories']]
        .join(elevation_df)
        .join(review_df)
        .join(cat_df)
        .join(bool_df)
        .join(mult_df)
        .sort_index(axis=1))
print('Done Joining.')

print(business_json_df.head(10))
print(business_json_df.shape)
print(business_json_df.columns)

# Split data into train and test.
msk = np.random.rand(len(business_json_df)) <= 0.8
train = business_json_df[msk]
test = business_json_df[~msk]

train.to_csv('yelp_dataset/businesses_train.csv')
test.to_csv('yelp_dataset/businesses_test.csv')

print('Done.')
