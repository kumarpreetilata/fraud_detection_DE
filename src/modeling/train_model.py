import os
import logging
import pandas as pd
from azure.storage.blob import BlobServiceClient
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Azure Blob Storage configuration
AZURE_BLOB_CONNECTION_STRING = os.getenv("AZURE_BLOB_CONNECTION_STRING")
BLOB_SERVICE_CLIENT = BlobServiceClient.from_connection_string(AZURE_BLOB_CONNECTION_STRING)
CONTAINER_NAME = "fraud-events"  # The container where transformed data files are stored

def load_transformed_data(file_path):
    """Load transformed data from Azure Blob Storage."""
    try:
        blob_client = BLOB_SERVICE_CLIENT.get_blob_client(container=CONTAINER_NAME, blob=file_path)
        downloaded_blob = blob_client.download_blob().readall()
        data = pd.read_csv(downloaded_blob)
        logger.info(f"Transformed data loaded successfully from {file_path}.")
        return data
    except Exception as e:
        logger.error(f"Failed to load transformed data from {file_path}: {str(e)}")
        return None

def train_model(data):
    """Train the fraud detection model."""
    try:
        # Separate features and target variable
        X = data.drop(columns=['is_fraud'])  # Features
        y = data['is_fraud']  # Target variable

        # Split data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Train a Random Forest Classifier
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        # Make predictions
        y_pred = model.predict(X_test)

        # Evaluate the model
        logger.info("Model evaluation:")
        logger.info(classification_report(y_test, y_pred))
        accuracy = accuracy_score(y_test, y_pred)
        logger.info(f"Model accuracy: {accuracy:.2f}")

        return model
    except Exception as e:
        logger.error(f"Failed to train model: {str(e)}")
        return None

def save_model(model, model_name="fraud_detection_model.pkl"):
    """Save the trained model to Azure Blob Storage."""
    try:
        # Save the model using joblib
        joblib.dump(model, model_name)
        
        # Upload the model to Azure Blob Storage
        blob_client = BLOB_SERVICE_CLIENT.get_blob_client(container=CONTAINER_NAME, blob=model_name)
        
        with open(model_name, "rb") as file:
            blob_client.upload_blob(file, overwrite=True)
        
        logger.info(f"Model saved successfully to {model_name}.")
    except Exception as e:
        logger.error(f"Failed to save model: {str(e)}")

def main():
    """Main function to execute the model training process."""
    # Specify the transformed data file to process
    transformed_data_file = "data/transformed/transaction_event_1.csv"  # Adjust based on your file names

    # Load transformed data
    data = load_transformed_data(transformed_data_file)
    
    if data is not None:
        # Train the model
        model = train_model(data)
        
        if model is not None:
            # Save the trained model
            save_model(model)

if __name__ == "__main__":
    main()
