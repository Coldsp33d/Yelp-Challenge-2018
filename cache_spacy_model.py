import pickle
from business_suggestion import DocLite
import pandas as pd
import spacy

print('Initializing SpaCy model.')
nlp = spacy.load('en_core_web_md')

print('Caching category vectors.')
catmap = pd.concat([pd.read_csv(
           'yelp_dataset/catmap_{}.csv'.format(typ), header=None, index_col=[0], squeeze=True
    	) for typ in ('Regional', 'Svd')]).to_dict()

catset = set(catmap.keys()).union({
	'Chinese', 'Asian Fusion', 'Noodles', 'Beer', 'Vietnamese', 'Bar and Grill',
	'Tacos', 'Sandwiches', 'Pizza', 'Pasta', 'Lasagna'})
dct = {c: DocLite(c, nlp(c).vector) for c in catset}

pickle.dump(dct, open('models/nlplite', 'wb'))