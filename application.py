from flask import Flask, jsonify, render_template, request, flash
import pickle
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import json
import os
from werkzeug.utils import secure_filename
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

application = Flask(__name__)
app = application

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}

# Create uploads directory if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Load models with error handling
try:
    # Load scaler
    with open('models/scaler.pkl', 'rb') as f:
        scaler = pickle.load(f)
    
    # Load the model (RandomForestRegressor)
    with open('models/randomforest.pkl', 'rb') as f:
        model = pickle.load(f)
    
    logger.info("Models loaded successfully!")
except Exception as e:
    logger.error(f"Error loading models: {str(e)}")
    raise Exception("Failed to load models. Please ensure model files exist.")

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/predict", methods=['GET', 'POST'])
def predictdata():
    if request.method == "POST":
        try:
            # Get form data
            data = {
                'age': float(request.form.get('age', 0)),
                'annual_income': float(request.form.get('annual_income', 0)),
                'monthly_expenses': float(request.form.get('monthly_expenses', 0)),
                'old_dependents': int(request.form.get('old_dependents', 0)),
                'young_dependents': int(request.form.get('young_dependents', 0)),
                'occupants_count': int(request.form.get('occupants_count', 0)),
                'house_area': float(request.form.get('house_area', 0)),
                'loan_tenure': 12,  # Fixed value from dataset
                'loan_installments': int(request.form.get('loan_installments', 0)),
                'type_of_house_T1': int(request.form.get('type_of_house', 0)),
                'sex_M': int(request.form.get('sex', 0))
            }
            
            # Input validation
            errors = []
            if data['age'] <= 0:
                errors.append("Age must be a positive number")
            if data['annual_income'] <= 0:
                errors.append("Annual income must be a positive number")
            if data['monthly_expenses'] <= 0:
                errors.append("Monthly expenses must be a positive number")
            if data['old_dependents'] < 0:
                errors.append("Number of old dependents cannot be negative")
            if data['young_dependents'] < 0:
                errors.append("Number of young dependents cannot be negative")
            if data['occupants_count'] <= 0:
                errors.append("Number of household occupants must be at least 1")
            if data['house_area'] <= 0:
                errors.append("House area must be a positive number")
            if data['loan_installments'] < 12 or data['loan_installments'] > 50:
                errors.append("Loan installments must be between 12 and 50")
            
            if errors:
                raise ValueError(". ".join(errors))
            
            # Add missing features with default values
            default_features = {
                'Id': 0,
                'home_ownership': 1.0,  # Based on training data
                'type_of_house_T2': 0,
                'sex_TG': 0
            }
            
            # Update data with default features
            data.update(default_features)
            
            # Define feature order exactly as in training data
            feature_order = [
                'old_dependents',
                'loan_installments',
                'loan_tenure',
                'home_ownership',
                'young_dependents',
                'monthly_expenses',
                'annual_income',
                'age',
                'house_area',
                'Id',
                'occupants_count',
                'type_of_house_T1',
                'type_of_house_T2',
                'sex_M',
                'sex_TG'
            ]
            
            # Create DataFrame in the exact order as training data
            features = pd.DataFrame([data], columns=feature_order)
            
            # Scale features
            scaled_features = scaler.transform(features)
            
            # Make prediction
            prediction = model.predict(scaled_features)[0]
                
            # Format the prediction result
            prediction_result = {
                'prediction': float(prediction),
                'status': 'success',
                'message': 'Loan amount prediction successful'
            }
            
            logger.info(f"Prediction successful: {prediction_result}")
            
            # Return the prediction as a rendered template
            return render_template('result.html', prediction=prediction_result)
            
        except ValueError as ve:
            logger.error(f"Value error: {str(ve)}")
            error_msg = str(ve)
            return render_template('error.html', error=error_msg), 400
            
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            error_msg = "Error processing prediction. Please try again."
            return render_template('error.html', error=error_msg), 500
    
    else:
        return render_template('index.html')
@app.route("/upload", methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Process the uploaded file
            df = pd.read_csv(filepath)
            # Add your file processing logic here
            
            return jsonify({
                'status': 'success',
                'message': 'File uploaded and processed successfully'
            })
        except Exception as e:
            logger.error(f"File processing error: {str(e)}")
            return jsonify({
                'error': str(e),
                'status': 'error',
                'message': 'Error processing file'
            }), 500
    else:
        return jsonify({'error': 'Invalid file type'}), 400

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_server_error(e):
    logger.error(f"Internal server error: {str(e)}")
    return render_template('error.html', error="Internal server error"), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)