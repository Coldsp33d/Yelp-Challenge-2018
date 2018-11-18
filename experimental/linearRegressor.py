from sklearn.linear_model import LinearRegression
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler, MinMaxScaler


#Load the Training Data
train_df = pd.read_csv("yelp_dataset/businesses_train.csv")
res_train = train_df['rating'].values
trains_df = train_df.drop(['business_id', 'categories', 'rating', 'id'], axis=1)

#Scale and fit the training data using standard scaler
scalar = StandardScaler()
train_data = trains_df.values
train_data[np.isnan(train_data)] = 0
train_data = scalar.fit_transform(train_data)
res_train = (res_train-res_train.min())*10/(res_train.max()-res_train.min())

#Applying linear regression on the data
reg = LinearRegression().fit(train_data, res_train)

test_df = pd.read_csv("yelp_dataset/businesses_test.csv")
res_test = test_df['rating'].values
test_df = test_df.drop(['business_id', 'categories', 'rating', 'id'], axis=1)
testdata = test_df.values

testdata[np.isnan(testdata)] = 0

testdata = scalar.transform(testdata)


res_test = (res_test-res_test.min())*10/(res_test.max()-res_test.min())

print("R2 Score is", reg.score(testdata, res_test))

print("Mean Squared Error is ", mean_squared_error(reg.predict(testdata), res_test))
#R2 Score is 0.051046085678
#Mean Squared Error is  1.2652887272


# objects = ('PriceRangeOne','PriceRangeTwo','PriceRangeThree','PriceRabgeFour', 'BikeParking', 'BusinessAcceptsCreditCards', 'Caters', 'GoodForKids', 'HasTV', 'OutdoorSeating', 'RestaurantsDelivery', 'RestaurantsGoodForGroups', 'RestaurantsReservations', 'RestaurantsTableService', 'RestaurantsTakeOut', 'WheelchairAccessible', 'average', 'beer_and_wine', 'breakfast', 'brunch', 'casual', 'casual_attire', 'classy', 'dessert', 'dinner', 'divey', 'dressy', 'elevation', 'formal', 'free', 'full_bar', 'garage', 'hipster', 'intimate', 'latenight', 'lot', 'loud', 'lunch', 'no', 'none', 'paid', 'quiet', 'romantic', 'street', 'touristy', 'trendy', 'upscale', 'valet', 'validated', 'very_loud')
# plt.barh(y_pos, performance, align='center', alpha=0.5)
# plt.yticks(y_pos, objects)
# coef = np.std(train_data, 0)*reg.coef_