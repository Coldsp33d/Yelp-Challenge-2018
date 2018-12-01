from flask import Flask, render_template
import joblib
import numpy as np
app = Flask(__name__)

@app.route("/")
def hello():
    return render_template('index.html')

@app.route('/predict')
def predict():
	try:
		#this is a single line comment
		clf = joblib.load('models/model')
		input = [[np.nan, 0.00000000e+00, 1.00000000e+00,np.nan,1.00000000e+00, 1.00000000e+00, 6.50445558e-01, 0.00000000e+00,9.69024436e-01, 0.00000000e+00, 1.00000000e+00, 5.31537743e-01, 1.00000000e+00, np.nan, 1.00000000e+00, np.nan, np.nan, 1.07600000e+03]]
		output = clf.predict(input)
		return str(output[0])
	except Exception as e:
		return str(e)


if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0', port=80)
