import os
import logging
import pandas as pd
from azure.storage.blob import BlobServiceClient
from sklearn.ensemble import IsolationForest
import pickle
from azure.identity import DefaultAzureCredential

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Azure Blob Storage configuration
AZURE_BLOB_CONNECTION_STRING = os.getenv("AZURE_BLOB_CONNECTION_STRING")
BLOB_SERVICE_CLIENT = BlobServiceClient.from_connection_string(AZURE_BLOB_CONNECTION_STRING)
CONTAINER_NAME = "fraud-events"  # The container where event data files are stored

# Load the model from the Blob Storage
def load_model(model_path):
    """Load the trained Isolation Forest model from Azure Blob Storage."""
    try:
        blob_client = BLOB_SERVICE_CLIENT.get_blob_client(container=CONTAINER_NAME, blob=model_path)
        model_data = blob_client.download_blob().readall()
        
        # Load the model using pickle
        model = pickle.loads(model_data)
        logger.info("Model loaded successfully.")
        return model
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        return None

def predict_fraud(model, data):
    """Predict fraud using the Isolation Forest model."""
    try:
        predictions = model.predict(data)
        # Convert predictions to a DataFrame for easier handling
        results = pd.DataFrame(data)
        results['fraud_prediction'] = predictions
        logger.info("Fraud predictions made successfully.")
        return results
    except Exception as e:
        logger.error(f"Failed to make predictions: {str(e)}")
        return None

def load_event_data(event_data_path):
    """Load event data from Azure Blob Storage."""
    try:
        blob_client = BLOB_SERVICE_CLIENT.get_blob_client(container=CONTAINER_NAME, blob=event_data_path)
        with open(event_data_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())

        # Assuming the data is in JSON format for event data
        data = pd.read_json(event_data_path)
        logger.info(f"Data loaded successfully from {event_data_path}.")
        return data
    except Exception as e:
        logger.error(f"Failed to load data from {event_data_path}: {str(e)}")
        return None

def main():
    """Main function to execute the fraud detection process."""
    
    # Specify the model and event data file paths
    model_path = "models/isolation_forest_model.pkl"  # Path to the saved model
    event_data_files = [
        "events/transaction_event_1.json",
        "events/transaction_event_2.json",
        # Add more event files as needed
    ]
    
    # Load the model
    model = load_model(model_path)
    
    if model is not None:
        for file_path in event_data_files:
            # Load event data
            event_data = load_event_data(file_path)
            
            if event_data is not None:
                # Prepare data for prediction
                feature_columns = ['amount', 'transaction_date', 'user_id']  # Example feature columns
                event_data['transaction_date'] = pd.to_datetime(event_data['transaction_date'])
                event_data['amount'] = event_data['amount'].astype(float)  # Ensure correct data type
                
                # Selecting relevant features for prediction
                prediction_data = event_data[feature_columns]
                
                # Make predictions
                results = predict_fraud(model, prediction_data)
                
                # Save results to Blob Storage
                output_file_path = f"data/processed/events/fraud_detection_results_{os.path.basename(file_path)}"
                save_results_to_blob(results, output_file_path)

def save_results_to_blob(results, output_file_path):
    """Save fraud detection results to Azure Blob Storage."""
    try:
        output_blob_client = BLOB_SERVICE_CLIENT.get_blob_client(container=CONTAINER_NAME, blob=output_file_path)
        
        # Save the DataFrame to CSV
        results.to_csv(output_file_path, index=False)
        
        with open(output_file_path, "rb") as data:
            output_blob_client.upload_blob(data, overwrite=True)
        
        logger.info(f"Fraud detection results saved successfully to {output_file_path}.")
    except Exception as e:
        logger.error(f"Failed to save results to {output_file_path}: {str(e)}")

if __name__ == "__main__":
    main()
