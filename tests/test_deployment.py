import os
import joblib
import numpy as np
import pandas as pd
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
MODEL_PATH = 'path_to_your_trained_model.joblib'  # Update with the actual path to your saved model

def load_model(model_path):
    """Load the trained model from the specified path."""
    try:
        model = joblib.load(model_path)
        logging.info("Model loaded successfully.")
        return model
    except Exception as e:
        logging.error(f"Error loading model: {e}")
        return None

def create_sample_input():
    """Create a sample input for testing the model."""
    # Create a sample input DataFrame
    sample_input = pd.DataFrame({
        'feature_1': [1.0],  # Replace with actual feature names and example values
        'feature_2': [0.5],
        'feature_3': [100],
        # Add more features as necessary based on your model's input
    })
    return sample_input

def test_model_prediction(model):
    """Test the model prediction on a sample input."""
    sample_input = create_sample_input()
    
    try:
        prediction = model.predict(sample_input)
        logging.info(f"Sample input: {sample_input.values}, Prediction: {prediction}")
    except Exception as e:
        logging.error(f"Error during prediction: {e}")

def main():
    """Main function to execute the deployment tests."""
    # Load the model
    model = load_model(MODEL_PATH)
    
    if model is not None:
        # Test the model prediction
        test_model_prediction(model)

if __name__ == "__main__":
    main()
