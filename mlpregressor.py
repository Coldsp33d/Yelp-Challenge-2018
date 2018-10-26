"""Multi Layer Perceptron for loading and tainig business and ratings data.
@author Koustav Mukherjee
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import Imputer
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score

def load_data(filepath):
	train_df = pd.read_csv(filepath)
	result = train_df['rating'].values
	train_df = train_df.drop(['business_id','categories','rating'], axis = 1)
	data = train_df.values
	return data, result


def classify_ratings(y):
    y_min = y.min()
    if(y_min < 0):
        y = y - y.min()
    y /= y.max()
    y *= 10
    return y #np.rint(y)

def train_model(X,y):
	#ACTIVATION_TYPES = ["identity", "logistic", "tanh", "relu"]
	mlp = MLPRegressor(solver='lbfgs', hidden_layer_sizes=50,max_iter=150, shuffle=True, random_state=1,activation='logistic')
	mlp.fit(X, y)
	return mlp
		
def reprort_accuracy(mlp, X_test, y_test):
    print("Accuracy Score : ", r2_score(y_test, mlp.predict(X_test)))

def reprort_rmse(mlp, X_test, y_test):
	print("RMSE Score : ", mean_squared_error(mlp.predict(X_test), y_test))

imp = Imputer(missing_values=np.nan, strategy='mean')
train_data = load_data('yelp_dataset/businesses_train.csv')
X = imp.fit_transform(train_data[0])
X = StandardScaler().fit_transform(X)
y = classify_ratings(train_data[1])

mlp = train_model(X,y)

test_data = load_data('yelp_dataset/businesses_test.csv')
X_test = imp.fit_transform(test_data[0])
y_test = classify_ratings(test_data[1])
reprort_accuracy(mlp, X_test, y_test)
reprort_rmse(mlp, X_test, y_test)