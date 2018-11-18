
# Create your first MLP in Keras
from keras.models import Sequential
from keras.layers import Dense
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from keras.utils import to_categorical

import numpy
# fix random seed for reproducibility
#Load the Training Data
train_df = pd.read_csv("yelp_dataset/businesses_train.csv")
res_train = train_df['rating'].values
trains_df = train_df.drop(['business_id', 'categories', 'rating', 'id'], axis=1)

#Scale and fit the training data using standard scaler
scalar = StandardScaler()
train_data = trains_df.values
train_data[np.isnan(train_data)] = 0
train_data = scalar.fit_transform(train_data)
res_train = (res_train-res_train.min())*9/(res_train.max()-res_train.min())
res_train = np.round(res_train)
res_train = to_categorical(res_train, num_classes=None)

model = Sequential()


model.add(Dense(60, input_dim=50, activation='relu'))
model.add(Dense(40, activation='relu'))
model.add(Dense(30, activation='relu'))
model.add(Dense(20, activation='relu'))
model.add(Dense(10, activation='sigmoid'))

# Compile model
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
# Fit the model
model.fit(train_data, res_train, epochs=150, batch_size=50)
# evaluate the model
#scores = model.evaluate(train_data, res_train)


test_df = pd.read_csv("yelp_dataset/businesses_test.csv")
res_test = test_df['rating'].values
test_df = test_df.drop(['business_id', 'categories', 'rating', 'id'], axis=1)
testdata = test_df.values

testdata[np.isnan(testdata)] = 0

testdata = scalar.transform(testdata)


res_test = (res_test-res_test.min())*9/(res_test.max()-res_test.min())
res_test = np.round(res_test)
res_test = to_categorical(res_train, num_classes=None)


predictions = model.predict(testdata)


#print("\n%s: %.2f%%" % (model.metrics_names[1], scores[1]*100))