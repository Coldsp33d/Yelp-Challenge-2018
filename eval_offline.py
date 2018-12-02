from transform_business_preferences import (
	NotEnoughDataException, CAT_LABEL, HOW, cols, model, suggest_business_attributes)
import pandas as pd
import numpy as np

import os 
import joblib
import random

# Sample a few records
# Randomly drop features from these records
# Predict new, if it is higher, discard
# Run through phase 2, update and predict again
# Report all those with increased suggestions

# SEED = 0, ACCURACY = 79.25
# SEED = 42,
# SEED = 1337,

def transform_df(df, fdict):
    return df.drop(fdict.keys(), axis=1).join(df.apply(fdict))


SAMPLE_SIZE = 1000
df_ = (pd.read_csv('yelp_dataset/businesses_withCluster_{}.csv'.format(HOW))
             .drop(['business_id', 'categories', 'rating'], 1)
             .dropna(subset=[CAT_LABEL])
             .sample(n=SAMPLE_SIZE * 3, seed=42))

preds1 = model.clf.predict(transform_df(df_, model.fdict).reindex(cols, axis=1).values)

records = df_.agg(lambda x: x.dropna().to_dict(), axis=1).tolist()

# Randomly remove anywhere between 2 and 4 non-null attributes.
random.seed(0)
for r in records:
    r.update(dict.fromkeys(random.choices(list(r.keys() - {CAT_LABEL}), k=random.randint(2, 4)), np.nan))    

dropped_df = pd.DataFrame(records)
dropped_df = dropped_df.pipe(transform_df, fdict=model.fdict).reindex(cols, axis=1)

preds2 = model.clf.predict(dropped_df.values)
print('Businesses with improved ratings after feature dropout: {} (out of {})'.format((preds2 >= preds1).sum(), len(preds2)))

# Drop every invalid row and take the first X number of valid businesses.
idx = np.random.choice(np.arange(len(df_))[preds2 < preds1], SAMPLE_SIZE, replace=False)
df_ = df_.iloc[idx]
preds1 = preds1[idx]
preds2 = preds2[idx]

records_filtered_suggested_attributes = {}
for i, (r, p1, p2) in enumerate(zip(records, preds1, preds2)):
	if p1 > p2:
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
print("Average Improvement:", (np.sign(diff) * (diff ** 2)).mean() ** .5)
