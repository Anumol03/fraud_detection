# liver_prediction/utils.py
import joblib
import os



def load_model():
    model_path = 'logistic_regression_model_fraud.pkl'  # Use forward slashes or double backslashes
    return joblib.load(model_path)