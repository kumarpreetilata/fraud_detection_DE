import os
import pandas as pd
import logging
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Azure Blob Storage configuration
AZURE_BLOB_CONNECTION_STRING = os.getenv("AZURE_BLOB_CONNECTION_STRING")
BLOB_SERVICE_CLIENT = BlobServiceClient.from_connection_string(AZURE_BLOB_CONNECTION_STRING)
CONTAINER_NAME = "fraud-events"  # The container where event data files are stored

def load_data_from_blob(file_path):
    """Load data from Azure Blob Storage based on file format."""
    try:
        blob_client = BLOB_SERVICE_CLIENT.get_blob_client(container=CONTAINER_NAME, blob=file_path)
        with open(file_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())
        
        if file_path.endswith(".csv"):
            data = pd.read_csv(file_path)
        elif file_path.endswith(".json"):
            data = pd.read_json(file_path)
        elif file_path.endswith(".xml"):
            data = pd.read_xml(file_path)
        else:
            logger.error("Unsupported file format.")
            return None

        logger.info(f"Data loaded successfully from {file_path}.")
        return data
    except Exception as e:
        logger.error(f"Failed to load data from {file_path}: {str(e)}")
        return None

def load_event_data(event_data_path):
    """Load event data from Azure Blob Storage."""
    return load_data_from_blob(event_data_path)

def clean_and_transform_data(df):
    """Perform data cleaning and transformation on the DataFrame."""
    try:
        logger.info("Starting data cleaning and transformation...")
        
        # Drop duplicates
        df.drop_duplicates(inplace=True)
        
        # Fill missing values - assuming 'amount' is a critical field
        df['amount'].fillna(0, inplace=True)
        
        # Convert 'transaction_date' to datetime format
        if 'transaction_date' in df.columns:
            df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')
        
        # Filter out transactions with negative amounts (if applicable)
        df = df[df['amount'] >= 0]
        
        logger.info("Data cleaning and transformation completed.")
        return df
    except Exception as e:
        logger.error(f"Failed to clean and transform data: {str(e)}")
        return None

def save_transformed_data(df, output_file_path):
    """Save the transformed DataFrame to Azure Blob Storage."""
    try:
        output_blob_client = BLOB_SERVICE_CLIENT.get_blob_client(container=CONTAINER_NAME, blob=output_file_path)
        
        # Save the transformed DataFrame to CSV
        df.to_csv(output_file_path, index=False)
        
        with open(output_file_path, "rb") as data:
            output_blob_client.upload_blob(data, overwrite=True)
        
        logger.info(f"Transformed data saved successfully to {output_file_path}.")
    except Exception as e:
        logger.error(f"Failed to save transformed data to {output_file_path}: {str(e)}")

def main():
    """Main function to load, transform, and save data."""
    
    # Specify the paths to the event data files
    event_data_files = [
        "events/transaction_event_1.json",
        "events/transaction_event_2.json",
        # Add more event files as needed
    ]
    
    for file_path in event_data_files:
        # Load event data from Blob
        event_data = load_event_data(file_path)
        
        if event_data is not None:
            # Clean and transform event data
            transformed_data = clean_and_transform_data(event_data)
            
            # Save transformed data back to Blob
            output_file_path = f"data/processed/events/transformed_{os.path.basename(file_path)}"
            if transformed_data is not None:
                save_transformed_data(transformed_data, output_file_path)

if __name__ == "__main__":
    main()
