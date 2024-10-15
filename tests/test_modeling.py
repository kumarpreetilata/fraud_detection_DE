import logging
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
MODEL_PATH = 'path_to_your_trained_model.joblib'  # Update with the actual path to your saved model

def create_sample_data():
    """Create a sample dataset for testing the model."""
    data = {
        'feature_1': np.random.rand(100),
        'feature_2': np.random.rand(100),
        'feature_3': np.random.randint(1, 100, size=100),
        'is_fraud': np.random.choice([0, 1], size=100)  # Binary classification target
    }
    return pd.DataFrame(data)

def train_model(data):
    """Train a Random Forest model on the provided data."""
    X = data.drop('is_fraud', axis=1)
    y = data['is_fraud']
    
    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)
    
    # Save the trained model
    joblib.dump(model, MODEL_PATH)
    logging.info(f"Model trained and saved to {MODEL_PATH}.")
    
    return model, X_test, y_test

def test_model_prediction(model, X_test, y_test):
    """Test the model's prediction capabilities."""
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    logging.info(f"Model accuracy: {accuracy:.2f}")
    
    # Validate predictions format
    if predictions.ndim != 1 or len(predictions) != len(y_test):
        logging.error("Prediction format is incorrect.")
        return False

    return True

def main():
    """Main function to execute the modeling tests."""
    # Create sample data
    sample_data = create_sample_data()
    
    # Train the model
    model, X_test, y_test = train_model(sample_data)
    
    # Test model prediction
    prediction_success = test_model_prediction(model, X_test, y_test)
    
    if prediction_success:
        logging.info("Model testing completed successfully.")
    else:
        logging.error("Model testing failed.")

if __name__ == "__main__":
    main()
