from transform_business_preferences import (
	NotEnoughDataException, CAT_LABEL, HOW, cols, suggest_business_attributes)

from utils import str2bool

import pandas as pd
import numpy as np

import sys
import os 
import joblib
import random
import argparse 

# Program flow:
# 	1. Sample a few records
# 	2. Randomly drop features from these records
# 	3. Predict new, if it is higher, discard
# 	4. Run through phase 2, update and predict again
# 	5. Report all those with increased suggestions

def transform_df(df, fdict):
    return df.drop(fdict.keys(), axis=1).join(df.apply(fdict))


if __name__ == '__main__':
	SAMPLE_SIZE = int(sys.argv[1])
	SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 0

	parser = argparse.ArgumentParser(description='Business Success Prediction - Offline Evaluation Script.')
	parser.add_argument('--randomDropout', 
	                    required=False,
	                    type=str2bool,
	                    nargs='?',
	                    const=True, 
	                    default=False,
	                    help="Randomly drop attributes in samples before suggestion.")

	args = vars(parser.parse_args())

	df_ = (pd.read_csv('yelp_dataset/businesses_withOtherBusinesses_withCluster_{}_test.csv'.format(HOW))
	             .drop(['business_id', 'categories', 'rating'], 1)
	             .dropna(subset=[CAT_LABEL])
	             .sample(n=SAMPLE_SIZE, random_state=SEED))

	model = model = joblib.load('models/model_withCluster_{}_train'.format(HOW))
	preds1 = model.clf.predict(transform_df(df_, model.fdict).reindex(cols, axis=1).values)

	records = df_.agg(lambda x: x.dropna().to_dict(), axis=1).tolist()

	if args['randomDropout']:
		# Randomly remove anywhere between 2 and 4 non-null attributes
		random.seed(SEED)
		for r in records:
		    r.update(dict.fromkeys(random.choices(list(r.keys() - {CAT_LABEL}), k=random.randint(2, 4)), np.nan))    

		dropped_df = pd.DataFrame(records)
		dropped_df = dropped_df.pipe(transform_df, fdict=model.fdict).reindex(cols, axis=1)

		preds2 = model.clf.predict(dropped_df.values)
		print('Businesses with improved ratings after feature dropout: {} (out of {})'
				.format((preds2 >= preds1).sum(), len(preds2)))

		# Drop every invalid row and take the first X number of valid businesses.
		idx = np.random.choice(np.arange(len(df_))[preds2 < preds1], SAMPLE_SIZE, replace=False)
		df_ = df_.iloc[idx]
		preds1 = preds1[idx]
		preds2 = preds2[idx]
	else:
		print("Size of testing sample:", len(df_))
		preds2 = preds1

	records_filtered_suggested_attributes = {}
	for i, (r, p1, p2) in enumerate(zip(records, preds1, preds2)):
		if p1 >= p2:
			try:
				records_filtered_suggested_attributes[i] = suggest_business_attributes(r, r[CAT_LABEL], p2)
			except NotEnoughDataException:
				pass

	suggested_df = (transform_df(pd.DataFrame.from_dict(records_filtered_suggested_attributes, orient='index'), model.fdict)
						.reindex(index=pd.np.arange(df_.shape[0]), columns=cols))
	preds3 = model.clf.predict(suggested_df.values.tolist())

	m = suggested_df.isna().all(1)
	preds1, preds2, preds3 = preds1[~m], preds2[~m], preds3[~m]
	diff = preds3 - preds2

	print("Accuracy: {}%".format((preds3 > preds2).mean() * 100))
	print("Average Improvement (+ve examples):", diff[diff > 0].mean() ** .5)
