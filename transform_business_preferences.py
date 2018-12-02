import copy
import pandas as pd
import joblib
from utils import NlpLite
import os

CAT_LABEL, HOW = [('catRegion_label', 'Regional'), ('cat152_label', 'Svd')][1]  # Change to [0] for Regional

nlp = NlpLite(os.path.join(os.path.dirname(__file__), 'models/nlplite'))

df = (pd.read_csv(os.path.join(os.path.dirname(__file__), 'yelp_dataset/businesses_withCluster_{}.csv'.format(HOW)))
        .drop('business_id', 1)
        .dropna(subset=[CAT_LABEL]))
		
model = joblib.load(os.path.join(os.path.dirname(__file__), 'models/model_withCluster_{}'.format(HOW)))

catmap = pd.read_csv(
        os.path.join(os.path.dirname(__file__), 'yelp_dataset/catmap_{}.csv'.format(HOW)), header=None, index_col=[0], squeeze=True
    ).to_dict()
	
cols = (pd.read_csv(os.path.join(os.path.dirname(__file__), 'yelp_dataset/businesses_withOtherBusinesses_withCluster_{}.csv'.format(HOW)), nrows=1)
          .drop(['business_id', 'categories', 'rating'], axis=1)
          .columns
          .tolist())

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