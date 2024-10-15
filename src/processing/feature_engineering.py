import os
import logging
import pandas as pd
from azure.storage.blob import BlobServiceClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Azure Blob Storage configuration
AZURE_BLOB_CONNECTION_STRING = os.getenv("AZURE_BLOB_CONNECTION_STRING")
BLOB_SERVICE_CLIENT = BlobServiceClient.from_connection_string(AZURE_BLOB_CONNECTION_STRING)
CONTAINER_NAME = "fraud-events"  # The container where event data files are stored

def load_event_data(file_path):
    """Load event data from Azure Blob Storage."""
    try:
        blob_client = BLOB_SERVICE_CLIENT.get_blob_client(container=CONTAINER_NAME, blob=file_path)
        downloaded_blob = blob_client.download_blob().readall()
        
        # Determine the format and load accordingly
        if file_path.endswith('.json'):
            data = pd.read_json(downloaded_blob)
        elif file_path.endswith('.csv'):
            data = pd.read_csv(downloaded_blob)
        elif file_path.endswith('.xml'):
            data = pd.read_xml(downloaded_blob)
        else:
            logger.error("Unsupported file format.")
            return None
        
        logger.info(f"Data loaded successfully from {file_path}.")
        return data
    except Exception as e:
        logger.error(f"Failed to load data from {file_path}: {str(e)}")
        return None

def extract_features(data):
    """Perform feature engineering on the input data."""
    try:
        # Example feature engineering: Create new features
        data['transaction_date'] = pd.to_datetime(data['transaction_date'])
        data['transaction_hour'] = data['transaction_date'].dt.hour
        data['transaction_day'] = data['transaction_date'].dt.day
        data['transaction_month'] = data['transaction_date'].dt.month
        
        # Create a binary feature for high transaction amount
        data['high_transaction'] = data['amount'].apply(lambda x: 1 if x > 1000 else 0)
        
        logger.info("Features extracted successfully.")
        return data
    except Exception as e:
        logger.error(f"Failed to extract features: {str(e)}")
        return None

def save_transformed_data(data, output_file_path):
    """Save the transformed data to Azure Blob Storage."""
    try:
        output_blob_client = BLOB_SERVICE_CLIENT.get_blob_client(container=CONTAINER_NAME, blob=output_file_path)
        
        # Save the DataFrame to CSV
        data.to_csv(output_file_path, index=False)
        
        with open(output_file_path, "rb") as file:
            output_blob_client.upload_blob(file, overwrite=True)
        
        logger.info(f"Transformed data saved successfully to {output_file_path}.")
    except Exception as e:
        logger.error(f"Failed to save transformed data to {output_file_path}: {str(e)}")

def main():
    """Main function to execute the feature engineering process."""
    
    # Specify the event data files to process
    event_data_files = [
        "events/transaction_event_1.json",
        "events/transaction_event_2.csv",
        # Add more event files as needed
    ]
    
    for file_path in event_data_files:
        # Load event data
        event_data = load_event_data(file_path)
        
        if event_data is not None:
            # Extract features
            transformed_data = extract_features(event_data)
            
            if transformed_data is not None:
                # Specify the output path for transformed data
                output_file_path = f"data/transformed/{os.path.basename(file_path)}"
                save_transformed_data(transformed_data, output_file_path)

if __name__ == "__main__":
    main()
