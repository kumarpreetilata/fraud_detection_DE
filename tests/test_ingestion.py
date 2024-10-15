import os
import json
import logging
import pandas as pd
from azure.storage.blob import BlobServiceClient, BlobServiceError

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Azure Blob Storage configuration
BLOB_CONNECTION_STRING = os.getenv("BLOB_CONNECTION_STRING", "DefaultEndpointsProtocol=https;AccountName=myblobstorageaccount;AccountKey=myBlobStorageKey;EndpointSuffix=core.windows.net")
BLOB_CONTAINER_NAME = os.getenv("BLOB_CONTAINER_NAME", "fraud-events")

def test_blob_ingestion():
    """Test data ingestion from Azure Blob Storage."""
    try:
        # Create a Blob Service Client
        blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)
        
        # Get the specified container
        container_client = blob_service_client.get_container_client(BLOB_CONTAINER_NAME)
        
        # List blobs in the container
        blob_list = container_client.list_blobs()
        
        for blob in blob_list:
            # Download blob data
            blob_client = container_client.get_blob_client(blob)
            downloaded_blob = blob_client.download_blob().readall()
            
            # Deserialize JSON data
            event_data = json.loads(downloaded_blob)
            logging.info(f"Successfully ingested blob: {blob.name} with data: {event_data}")

            # Validate the structure of the ingested data
            if not validate_event_data(event_data):
                logging.error(f"Invalid data structure for blob: {blob.name}")
                return False

        logging.info("All blobs ingested successfully.")
        return True

    except BlobServiceError as e:
        logging.error(f"Blob service error: {e}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error during blob ingestion: {e}")
        return False

def validate_event_data(event_data):
    """Validate the structure of the ingested event data."""
    required_keys = ['transaction_id', 'amount', 'timestamp', 'is_fraud']  # Adjust according to your schema
    return all(key in event_data for key in required_keys)

def main():
    """Main function to execute the ingestion tests."""
    success = test_blob_ingestion()
    if success:
        logging.info("Data ingestion test completed successfully.")
    else:
        logging.error("Data ingestion test failed.")

if __name__ == "__main__":
    main()
