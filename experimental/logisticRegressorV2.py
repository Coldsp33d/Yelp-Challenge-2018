from sklearn.linear_model import LogisticRegression
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
#df_ = pd.read_csv("yelp_dataset/businesses_withOtherBusinesses_withCluster_Regional.csv")

df_ = pd.read_csv("yelp_dataset/businesses_withOtherBusinesses_withCluster_Svd.csv")
df_.drop(['business_id', 'categories'], axis=1, inplace=True)
df_[cat_cols] = df_[cat_cols].apply(freq_encode)

y = MinMaxScaler((1, 10)).fit_transform(df_.pop('rating')[:, None])
X = df_.values

y = np.round(y)
#print(y)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.1, random_state=42)



X_train[np.isnan(X_train)] = 0
X_test[np.isnan(X_test)] = 0

clf = LogisticRegression(random_state=0, solver='lbfgs', multi_class='multinomial').fit(X_train, y_train)


print("R2 Score is", clf.score(X_test, y_test))

print("Mean Squared Error is ", mean_squared_error(clf.predict(X_test), y_test))

# R2 Score is 0.368112126925
# Mean Squared Error is  1.55412471986
