from flask import Flask, render_template, send_from_directory, request
import joblib
import numpy as np
import sys, os
import json
import requests
from flask import jsonify

sys.path.append(os.path.abspath('..'))
import transform_business_preferences

app = Flask(__name__)
model = joblib.load('../models/model_withCluster_Svd')

class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

@app.route("/")
def hello():
    return render_template('index.html')

@app.route('/predict', methods = ['POST'])
def predict():
	response = {}
	try:
		data = request.json
		print(data)
		prefrences = data['Attributes']
		for key in prefrences:
			if prefrences[key] == 'na':
				prefrences[key] = np.nan
				
		business_category = data['Category']
		most_similar_business_category, new = transform_business_preferences.preprocess_user_data(prefrences, business_category)
		print(new)
		business_predicted_rating = model.clf.predict([new.tolist()])[0]
		response['current_rating'] = str(business_predicted_rating)
		suggested_preferences = transform_business_preferences.suggest_business_attributes(prefrences, new['cat152_label'], business_predicted_rating)
		#print(business_preferences)
		response['suggested_preferences'] = suggested_preferences
		_, suggested = transform_business_preferences.preprocess_user_data(suggested_preferences, business_category)
		improved_rating = model.clf.predict([suggested.tolist()])[0]
		response['improved_rating'] = str(improved_rating)
		return jsonify(response)
	except Exception as e:
		response['error'] = str(e)
		raise InvalidUsage(response, status_code=500)

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)

@app.route('/elevation', methods = ['GET'])
def elevation():
	response = {}
	try:
		latlaongurl = "https://maps.googleapis.com/maps/api/geocode/json"
		location = user = request.args.get('location')
		PARAMS = {'address':location, 'key':'AIzaSyCPyJ1OvFgnfX_RsLq1mx0V8nooRyFONTQ'} 
		r = requests.get(url = latlaongurl, params = PARAMS)
		data = r.json() 
		latitude = data['results'][0]['geometry']['location']['lat'] 
		longitude = data['results'][0]['geometry']['location']['lng']
		
		locationstr = str(latitude) + "," + str(longitude)
		elevationurl = "https://maps.googleapis.com/maps/api/elevation/json"
		PARAMS_1 = {'locations':locationstr, 'key':'AIzaSyCPyJ1OvFgnfX_RsLq1mx0V8nooRyFONTQ'}
		r_1 = requests.get(url = elevationurl, params = PARAMS_1)
		data_1 = r_1.json()
		elevation = data_1['results'][0]['elevation']
		print(str(elevation))
		return str(elevation)
	except Exception as e:
		response['error'] = str(e)
		raise InvalidUsage(response, status_code=500)

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
	
if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0', port=80)
