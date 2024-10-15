import os
import json
import logging
from azure.identity import DefaultAzureCredential
from azure.mgmt.datafactory import DataFactoryManagementClient
from azure.mgmt.datafactory.models import (
    DataFactory,
    PipelineResource,
    DatasetResource,
    LinkedServiceResource,
    CopyActivity,
    BlobSink,
    BlobSource,
    AzureBlobStorageLinkedService,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Azure credentials and configuration
AZURE_SUBSCRIPTION_ID = os.getenv("AZURE_SUBSCRIPTION_ID")
RESOURCE_GROUP_NAME = os.getenv("RESOURCE_GROUP_NAME")
DATA_FACTORY_NAME = os.getenv("DATA_FACTORY_NAME")

# Data source configuration
DATA_SOURCES = {
    "transaction_csv": {
        "format": "CSV",
        "path": "data/raw/transactions/transaction_data.csv",
    },
    "transaction_json": {
        "format": "JSON",
        "path": "data/raw/transactions/transaction_data.json",
    },
    "transaction_xml": {
        "format": "XML",
        "path": "data/raw/transactions/transaction_data.xml",
    },
}

# Initialize Azure Data Factory client
credential = DefaultAzureCredential()
data_factory_client = DataFactoryManagementClient(credential, AZURE_SUBSCRIPTION_ID)

def create_linked_service():
    """Create a linked service to Azure Blob Storage."""
    try:
        linked_service_name = "AzureBlobStorageLinkedService"
        linked_service = AzureBlobStorageLinkedService(
            connection_string=os.getenv("AZURE_BLOB_CONNECTION_STRING")
        )
        
        data_factory_client.linked_services.create_or_update(
            RESOURCE_GROUP_NAME,
            DATA_FACTORY_NAME,
            linked_service_name,
            LinkedServiceResource(properties=linked_service)
        )
        logger.info("Linked service created successfully.")
    except Exception as e:
        logger.error(f"Failed to create linked service: {str(e)}")

def create_datasets():
    """Create datasets for each data source."""
    try:
        for name, config in DATA_SOURCES.items():
            dataset = {
                "name": name,
                "properties": {
                    "linked_service_name": {"reference_name": "AzureBlobStorageLinkedService"},
                    "folder": {"name": "transactions"},
                    "file_format": config["format"],
                    "path": config["path"],
                }
            }
            data_factory_client.datasets.create_or_update(
                RESOURCE_GROUP_NAME,
                DATA_FACTORY_NAME,
                name,
                DatasetResource(properties=dataset)
            )
            logger.info(f"Dataset '{name}' created successfully.")
    except Exception as e:
        logger.error(f"Failed to create datasets: {str(e)}")

def create_pipeline():
    """Create a pipeline for copying data from Blob storage to the Data Lake."""
    try:
        pipeline_name = "CopyDataPipeline"
        activities = []
        
        for source_name in DATA_SOURCES.keys():
            copy_activity = CopyActivity(
                name=f"CopyFrom{source_name.capitalize()}",
                source=BlobSource(),
                sink=BlobSink(),
                inputs=[{"reference_name": source_name}],
                outputs=[{"reference_name": "ProcessedTransactions"}]
            )
            activities.append(copy_activity)

        pipeline = PipelineResource(
            activities=activities,
            description="Pipeline to copy transaction data from Blob storage"
        )

        data_factory_client.pipelines.create_or_update(
            RESOURCE_GROUP_NAME,
            DATA_FACTORY_NAME,
            pipeline_name,
            pipeline
        )
        logger.info("Pipeline created successfully.")
    except Exception as e:
        logger.error(f"Failed to create pipeline: {str(e)}")

def main():
    """Main function to run the data factory setup."""
    create_linked_service()
    create_datasets()
    create_pipeline()

if __name__ == "__main__":
    main()
