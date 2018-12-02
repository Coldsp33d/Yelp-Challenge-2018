from flask import Flask, render_template, send_from_directory, request
import joblib
import numpy as np
import sys, os

sys.path.append(os.path.abspath('..'))
import transform_business_preferences

app = Flask(__name__)

@app.route("/")
def hello():
    return render_template('index.html')

@app.route('/predict', methods = ['POST'])
def predict():
	try:
		data = request.json
		print(data)
		print("Hello World!!")
		business_category = 'Italian' 
		business_preferences = {
			'Alcohol': 'none',
			'BikeParking':0,
			'BusinessAcceptsCreditCards':1,
			'Caters':0,
			'GoodForKids':0,
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
			'WiFi':'no',
			# CAT_LABEL: business_category
		}
		most_similar_business_category, new = transform_business_preferences.preprocess_user_data(business_preferences, business_category)
		print(new)
		print("Hello World!!")
		#this is a single line comment
		clf = joblib.load('../models/model')
		input = [[np.nan, 0.00000000e+00, 1.00000000e+00,np.nan,1.00000000e+00, 1.00000000e+00, 6.50445558e-01, 0.00000000e+00,9.69024436e-01, 0.00000000e+00, 1.00000000e+00, 5.31537743e-01, 1.00000000e+00, np.nan, 1.00000000e+00, np.nan, np.nan, 1.07600000e+03]]
		output = clf.predict(input)
		return str(output[0])
	except Exception as e:
		return str(e)

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)

if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0', port=80)
