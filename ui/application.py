from flask import Flask, render_template, send_from_directory, request
import joblib
import numpy as np
import sys, os
import json

sys.path.append(os.path.abspath('..'))
import transform_business_preferences

app = Flask(__name__)
model = joblib.load('../models/model_withCluster_Svd')

@app.route("/")
def hello():
    return render_template('index.html')

@app.route('/predict', methods = ['POST'])
def predict():
	try:
		data = request.json
		prefrences = data['Attributes']
		
		for key in prefrences:
			if prefrences[key] == 'na':
				prefrences[key] = np.nan
				
		business_category = data['Category']
		most_similar_business_category, new = transform_business_preferences.preprocess_user_data(prefrences, business_category)
		print(new)
		print("Hello World!!")
		business_predicted_rating = model.clf.predict([new.tolist()])[0]
		return str(business_predicted_rating)
	except Exception as e:
		return str(e)

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)

if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0', port=80)
