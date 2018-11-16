import pandas as pd

business_category = 'Vietnamese'

business_preferences = {
	'Alcohol': 'beer_and_wine',
	'BikeParking':0,
	'BusinessAcceptsCreditCards':1,
	'Caters':0,
	'GoodForKids':0,
	'HasTV':1,
	'NoiseLevel':'loud',
	'OutdoorSeating':1,
	'RestaurantsAttire':'formal',
	'RestaurantsDelivery':1,
	'RestaurantsGoodForGroups':0,
	'RestaurantsPriceRange2':2,
	'RestaurantsReservations':1,
	'RestaurantsTableService':0,
	'RestaurantsTakeOut':1,
	'WheelchairAccessible':0,
	'WiFi':'paid'
}

business_predicted_rating = 3.5 # This value will come from phase 1 of the project

suggestion_category = ['Alcohol','BikeParking','BusinessAcceptsCreditCards','Caters','GoodForKids','HasTV','NoiseLevel','OutdoorSeating','RestaurantsAttire','RestaurantsDelivery','RestaurantsGoodForGroups','RestaurantsPriceRange2','RestaurantsReservations','RestaurantsTableService','RestaurantsTakeOut','WheelchairAccessible','WiFi']

df_catmap = pd.read_csv('yelp_dataset\\catmap_Regional.csv', header=None)

cat_map = {}
for key,val in zip(df_catmap[0], df_catmap[1]):
	cat_map[key] = val

business_category_idx = cat_map[business_category]

df = pd.read_csv('yelp_dataset\\businesses_withCluster_Regional.csv')
all_businesses_in_category = df[df['catRegion_label'] == business_category_idx]
k = int(len(all_businesses_in_category) * 0.1) #Take top 10 percent of the ratings
all_better_businesses_in_category = all_businesses_in_category[all_businesses_in_category['stars'] > business_predicted_rating] #consider only ratings that are greater than the predicted business rating
best_k = all_better_businesses_in_category.nlargest(k,'stars',keep='first')


if(len(best_k) == 0):
	print("You are one of the best in your Category!!")

else:
	best_output = {}
	for category in suggestion_category:
		best_output[category] = best_k.groupby(category)['stars'].sum().reset_index().sort_values(category,ascending=False).iloc[0][category]
	diff = {}
	for key, value in best_output.items():
		if(business_preferences[key] != value):
			diff[key] = [business_preferences[key], value]
	print("These are the areas you can improve : ")
	#improved_df = pd.DataFrame(diff, index=['Improved'])
	improved_df = pd.DataFrame.from_dict(diff, orient='index', columns=['Current','Improved'])
	print(improved_df)