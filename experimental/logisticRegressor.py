from sklearn.linear_model import LogisticRegression
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler, MinMaxScaler

train_df = pd.read_csv("yelp_dataset/businesses_train.csv")
res_train = train_df['rating'].values
trains_df = train_df.drop(['business_id', 'categories', 'rating', 'id'], axis=1)

scalar = StandardScaler()
train_data = trains_df.values
train_data[np.isnan(train_data)] = 0

train_data = scalar.fit_transform(train_data)
res_train = (res_train-res_train.min())*10/(res_train.max()-res_train.min())
res_train = np.round(res_train)

clf = LogisticRegression(random_state=0, solver='lbfgs', multi_class='multinomial').fit(train_data, res_train)

test_df = pd.read_csv("yelp_dataset/businesses_test.csv")
res_test = test_df['rating'].values
test_df = test_df.drop(['business_id', 'categories', 'rating', 'id'], axis=1)
testdata = test_df.values

testdata[np.isnan(testdata)] = 0

testdata = scalar.transform(testdata)


res_test = (res_test-res_test.min())*10/(res_test.max()-res_test.min())
res_test = np.round(res_test)


print("R2 Score is", clf.score(testdata, res_test))

print("Mean Squared Error is ", mean_squared_error(clf.predict(testdata), res_test))

# R2 Score is 0.368112126925
# Mean Squared Error is  1.55412471986
