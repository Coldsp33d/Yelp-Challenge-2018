from sklearn.model_selection import (
	GridSearchCV, StratifiedKFold, train_test_split)
from sklearn.metrics import mean_squared_error, accuracy_score
from sklearn.preprocessing import StandardScaler, Imputer, MinMaxScaler
from scipy.sparse import csr_matrix

import pandas as pd
import joblib
import numpy as np
import xgboost as xgb
import sys
import os

def freq_encode(ser):
    return ser.map(ser.value_counts(normalize=True))

cat_cols = ['Alcohol', 'NoiseLevel', 'RestaurantsAttire', 'RestaurantsPriceRange2', 'WiFi']

df_ = pd.read_csv(sys.argv[1])
df_.drop(['business_id', 'categories'], axis=1, inplace=True)
df_[cat_cols] = df_[cat_cols].apply(freq_encode)

c = df_.select_dtypes(include=[object]).columns

y = MinMaxScaler((1, 10)).fit_transform(df_.pop('rating')[:, None])
X = df_.values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.1, random_state=42)

print('XGBoost Version:', xgb.__version__)

# Train XGB model using GridSearchCV.
parameters = {'nthread':[4], #when use hyperthread, xgboost may become slower
              'objective':['reg:linear'],
              'learning_rate': [0.25], #so called `eta` value
              'max_depth': [6],
              'min_child_weight': [11],
              'silent': [1],
              'subsample': [0.8],
              'colsample_bytree': [0.3, 0.7],
              'n_estimators': [500], #number of trees
              'seed': [1337]}

xgb_model = xgb.XGBRegressor()
clf = GridSearchCV(xgb_model, parameters, cv=5, n_jobs=5, scoring='r2', verbose=2, refit=True)

clf.fit(X_train, y_train)

preds = clf.predict(X_test)
print('Regressor RMSE:', mean_squared_error(preds, y_test) ** .5)
print("Best Params:",  clf.best_params_)

fname = (os.path.basename(sys.argv[1])
			.split('.')[0]
			.replace('businesses', 'model')
			.replace('_withOtherBusinesses', ''))

try:
	os.stat('models')
except FileNotFoundError:
	os.mkdir('models')

joblib.dump(clf, os.path.join('models', fname))

