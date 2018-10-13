#Author : Vamshi Chenna - Week 1

import pandas as pd


business_json_df = pd.read_json('yelp_academic_dataset_business.json', lines=True)

#Get the restuarant Data from the businesses
restuarantData = business_json_df[business_json_df.attributes.map(lambda x: not pd.isnull(x) and any(y.startswith('Restaurant') or y.startswith('Alcohol') for y in x.keys())) | business_json_df['categories'].astype(str).str.contains("Restaurants|Food|Restaurant|Bars", case=False) |  business_json_df.name.astype(str).str.contains("Restaurants|Restaurant", case=False)]
#Total Businesses Identified as Resturants : 115000


#Attributes-----------------------------------------------------------------------------------------
attrData = restuarantData.attributes.dropna().tolist

attrDF = pd.DataFrame(restuarantData.attributes.dropna().tolist())

#Gets the individual count for every attribute
attrCount = attrDF.count()

#To save into a csv file, use
# attrCount.to_csv('/home/vamshi/PycharmProjects/YelpChallenge/attrCount.csv')
#Sample Data
#RestaurantsGoodForGroups       53839
#RestaurantsPriceRange2        107120
#RestaurantsReservations        51363
#RestaurantsTableService        43325
#RestaurantsTakeOut             61206
#Smoking                         8103


#To Caliculate averages and attribute density,
attrDensity = attrDF.count(axis=1)

#Gets the number of business having attributes more than 1
attrDensity[attrDensity>1].size

#Get the average of attributes per business
attrDensity.mean()

#Avergage number of attributes per Resturant : 11.338933217616168
#Resturants which have atlest one attribute : 112919
#Restuarants having more than one attribute : 111549
#Resturants having more than three attributes : 101870
#Resturants having more than five attributes : 76988
#Resturants having more than ten attributes : 50864


#Categories-----------------------------------------------------------------------------------------
categories = restuarantData.categories.dropna().str.split(r'\s*,\s*', expand=True)

#Get the categories count per user
catcount = categories.count(axis=1)

#Get the mean of the no of categories
categories.count(axis=1).mean

#Gets the number of business having categories more than 1
catcount[catcount>1].size

#Average category per resturant : 4.0274109643857541
#Restuarants having atlest one category : 114954
#Restuarants having more than one category : 114390
#Restuarants having more than two categories : 82534

#Shopping	24503
#Beauty & Spas	15956
#Nightlife	12147
#Bars	10853
#Coffee & Tea	6936


#Reviews-----------------------------------------------------------------------------------------

#Average No of Reviews for a busineses : 43.107634782608699
#Minimum no of reviews for a resturant : 3

#Restuarants having atlest 10 reviews : 65719
#Restuarants having more than 15 reviews : 52183
#Restuarants having more than 20 reviews : 42111
#Resturants having more than 25 reviews : 36274
#Resturants having more than 30 reviews : 31881


business_json_df.review_count.mean()
