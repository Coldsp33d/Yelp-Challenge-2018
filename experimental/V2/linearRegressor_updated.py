from sklearn.linear_model import LinearRegression
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split

mappings = {}
def freq_encode(ser):
  assert ser.name, "Column name is empty, please ensure column names are populated."

  mapping = ser.value_counts(normalize=True)
  mappings[ser.name] = lambda x: x.map(mapping.to_dict())

  return ser.map(mapping)

cat_cols = ['Alcohol', 'NoiseLevel', 'RestaurantsAttire', 'RestaurantsPriceRange2', 'WiFi']
df_ = pd.read_csv("yelp_dataset/businesses_withOtherBusinesses_withCluster_Regional.csv")

#df_ = pd.read_csv("yelp_dataset/businesses_withOtherBusinesses_withCluster_Svd.csv")
df_.drop(['business_id', 'categories'], axis=1, inplace=True)
df_[cat_cols] = df_[cat_cols].apply(freq_encode)

y = MinMaxScaler((1, 10)).fit_transform(df_.pop('rating')[:, None])
X = df_.values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.1, random_state=42)

X_train[np.isnan(X_train)] = 0
X_test[np.isnan(X_test)] = 0


#Applying linear regression on the data
reg = LinearRegression().fit(X_train, y_train)

print("R2 Score is", reg.score(X_test, y_test))

print("Mean Squared Error is ", mean_squared_error(reg.predict(X_test), y_test))
#R2 Score is 0.051046085678
#Mean Squared Error is  1.2652887272


# objects = ('PriceRangeOne','PriceRangeTwo','PriceRangeThree','PriceRabgeFour', 'BikeParking', 'BusinessAcceptsCreditCards', 'Caters', 'GoodForKids', 'HasTV', 'OutdoorSeating', 'RestaurantsDelivery', 'RestaurantsGoodForGroups', 'RestaurantsReservations', 'RestaurantsTableService', 'RestaurantsTakeOut', 'WheelchairAccessible', 'average', 'beer_and_wine', 'breakfast', 'brunch', 'casual', 'casual_attire', 'classy', 'dessert', 'dinner', 'divey', 'dressy', 'elevation', 'formal', 'free', 'full_bar', 'garage', 'hipster', 'intimate', 'latenight', 'lot', 'loud', 'lunch', 'no', 'none', 'paid', 'quiet', 'romantic', 'street', 'touristy', 'trendy', 'upscale', 'valet', 'validated', 'very_loud')
# plt.barh(y_pos, performance, align='center', alpha=0.5)
# plt.yticks(y_pos, objects)
# coef = np.std(train_data, 0)*reg.coef_