from sklearn.preprocessing import MinMaxScaler

import copy
import pandas as pd
import joblib
from utils import NlpLite
import os

class NotEnoughDataException(Exception):
    pass

CAT_LABEL, HOW = [('catRegion_label', 'Regional'), ('cat152_label', 'Svd')][1]  # Change to [0] for Regional

nlp = NlpLite(os.path.join(os.path.dirname(__file__), 'models/nlplite'))

df = (pd.read_csv(os.path.join(os.path.dirname(__file__), 'yelp_dataset/businesses_withCluster_{}.csv'.format(HOW)))
        .drop('business_id', 1)
        .dropna(subset=[CAT_LABEL]))
df['rating'] = MinMaxScaler((1, 10)).fit_transform(df['rating'].values[:, None])
		
model = joblib.load(os.path.join(os.path.dirname(__file__), 'models/model_withCluster_{}'.format(HOW)))

catmap = pd.read_csv(
        os.path.join(os.path.dirname(__file__), 'yelp_dataset/catmap_{}.csv'.format(HOW)), header=None, index_col=[0], squeeze=True
    ).to_dict()
	
cols = (pd.read_csv(os.path.join(os.path.dirname(__file__), 'yelp_dataset/businesses_withOtherBusinesses_withCluster_{}.csv'.format(HOW)), nrows=1)
          .drop(['business_id', 'categories', 'rating'], axis=1)
          .columns
          .tolist())

# Attributes to suggest improvements on.
suggested_attributes_list = [
    'Alcohol',
    'BikeParking',
    'BusinessAcceptsCreditCards',
    'Caters',
    'GoodForKids',
    'HasTV',
    'NoiseLevel',
    'OutdoorSeating',
    'RestaurantsAttire',
    'RestaurantsDelivery',
    'RestaurantsGoodForGroups',
    'RestaurantsPriceRange2',
    'RestaurantsReservations',
    'RestaurantsTableService',
    'RestaurantsTakeOut',
    'WheelchairAccessible',
    'WiFi'
]

def preprocess_user_data(business_preferences, business_category):
    business_preferences = copy.deepcopy(business_preferences)
    catmap_keys = sorted(df[CAT_LABEL].map({v:k for k,v in catmap.items()}).unique())

    most_similar_business_category = business_category

    vecs1 = [nlp(c1) for c1 in business_category.split(',')]
    vecs2 = [nlp(c2) for c2 in catmap_keys]
    idx = pd.np.argmax([max(c1.similarity(c2) for c1 in vecs1) for c2 in vecs2])
    most_similar_business_category = catmap_keys[idx]

    print("Your business is most similar to the category:", most_similar_business_category, "({})".format(idx))

    # Update business_preferences dictionary to include category label for a more accurate prediction.
    business_preferences[CAT_LABEL] = idx
    
    new = pd.DataFrame(business_preferences, index=[0]).assign(category=[business_category])
    return (
        most_similar_business_category, 
        new.drop(model.fdict.keys(), 1).join(new.apply(model.fdict)).reindex(cols, axis=1).T.squeeze())


def suggest_business_attributes(business_preferences, business_category_label, business_predicted_rating):
    m = (df[CAT_LABEL].eq(business_category_label) 
     & df['RestaurantsPriceRange2']
            .sub(business_preferences.get('RestaurantsPriceRange2', 2.5))
            .abs()
            .lt(2))
    all_businesses_in_category = df[m]

    # consider only ratings that are greater than the predicted business rating
    all_better_businesses_in_category = all_businesses_in_category[
        all_businesses_in_category['rating'] > business_predicted_rating]

    # Take top 10 percent of the ratings, or 20 businesses, whichever is higher.
    k = max(20, int(len(all_better_businesses_in_category) * 0.1)) 

    best_k = (all_better_businesses_in_category
                .sort_values('rating', ascending=False).reset_index(drop=True))

    if not len(best_k):
        raise NotEnoughDataException("Not enough data for prediction.")

    best_output = {}
    for attribute in suggested_attributes_list:
        t = best_k.dropna(subset=[attribute])

        if t.empty:
            best_output[attribute] = pd.np.nan
        else:
            best_output[attribute] = (
                t.assign(rating=t.rating * 1/pd.np.arange(1, len(t)+1))
                  .groupby(attribute).rating
                  .sum()
                  .sort_values(ascending=False)
                  .index[0])

    diff = business_preferences.copy()
    diff.update(best_output)

    return diff
