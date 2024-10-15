import os
import logging
import joblib
from azure.storage.blob import BlobServiceClient
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Azure Blob Storage configuration
AZURE_BLOB_CONNECTION_STRING = os.getenv("AZURE_BLOB_CONNECTION_STRING")
BLOB_CONTAINER_NAME = "fraud-events"  # Name of the blob container
MODEL_BLOB_NAME = "fraud_detection_model.pkl"  # Name of the saved model in Blob Storage

def train_model(data):
    """Train a fraud detection model."""
    # Split data into features and target
    X = data.drop(columns=['is_fraud'])  # Assuming 'is_fraud' is the target column
    y = data['is_fraud']

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train a RandomForestClassifier model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate the model
    predictions = model.predict(X_test)
    report = classification_report(y_test, predictions)
    logger.info(f"Model evaluation report:\n{report}")

    return model

def save_model_to_blob(model):
    """Save the trained model to Azure Blob Storage."""
    try:
        # Serialize the model using joblib
        joblib.dump(model, MODEL_BLOB_NAME)

        # Upload the model to Blob Storage
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_BLOB_CONNECTION_STRING)
        blob_client = blob_service_client.get_blob_client(container=BLOB_CONTAINER_NAME, blob=MODEL_BLOB_NAME)

        with open(MODEL_BLOB_NAME, "rb") as model_file:
            blob_client.upload_blob(model_file, overwrite=True)
        
        logger.info(f"Model {MODEL_BLOB_NAME} deployed to Azure Blob Storage successfully.")
    except Exception as e:
        logger.error(f"Failed to save model to blob: {str(e)}")

def main():
    """Main function to train and deploy the model."""
    # Load your data for training (assuming data is in a suitable format)
    # You would replace this part with actual data ingestion code
    data = pd.read_csv("path/to/your/fraud_data.csv")  # Update with your data source

    # Train the model
    model = train_model(data)

    # Save the model to Azure Blob Storage
    save_model_to_blob(model)

if __name__ == "__main__":
    main()
