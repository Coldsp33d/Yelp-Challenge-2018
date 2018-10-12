#Pre-requisites for running this code. Please ensure that the Data folder is created and has the following two JSON files
# yelp_academic_dataset_business.json and altitude.csv

import pandas as pd

# Read the business yelp_academic_dataset_business.json into a dataframe
business_json_df = pd.read_json("Data\\yelp_academic_dataset_business.json", lines=True)

# Filter only the rows that are associated with a business
# Either the attributes column contain a key that starts with Restaurant or Alcohol
# Or the categories column contain a substring like Restaurant or Food or Bar
# Or name contains Restaurant
business_json_df = business_json_df[business_json_df.attributes.map(lambda x: not pd.isnull(x) and any(y.startswith('Restaurant') or y.startswith('Alcohol') for y in x.keys())) | business_json_df['categories'].astype(str).str.contains("Food|Restaurant|Bars", case=False) | business_json_df.name.astype(str).str.contains("Restaurant", case=False)]

# All the altitude information for each business id has been extracted from QGIS and has been stored in altitude.csv
# The altitude.csv contains business_id and elevation as two columns
# The below command joins the elevation column with other columns in business_json_df
elevation_df = pd.read_csv("Data\\altitude.csv")
business_json_df = business_json_df.set_index('business_id').join(elevation_df.set_index('business_id'))

# Saving the filtered data for future use
# We can decide whether we want this to be csv or json
business_json_df.to_csv("Data\\businesses.csv")