#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Set up Python environment
PYTHON_VERSION="3.9"  # Change this to your required Python version
VENV_NAME="fraud_detection_env"

# Create a virtual environment
echo "Creating virtual environment..."
python$PYTHON_VERSION -m venv $VENV_NAME

# Activate the virtual environment
echo "Activating virtual environment..."
source $VENV_NAME/bin/activate

# Install required packages
echo "Installing required packages..."
pip install --upgrade pip
pip install azure-eventhub azure-storage-blob pandas numpy scikit-learn jupyter pytest

# Optionally, install additional libraries for machine learning, if needed
# pip install tensorflow keras matplotlib seaborn

# Set up environment variables
echo "Setting up environment variables..."
export EVENT_HUB_CONNECTION_STRING="Endpoint=sb://myeventhubnamespace.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=mySharedAccessKey;"
export EVENT_HUB_NAME="fraudDetectionHub"
export BLOB_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=myblobstorageaccount;AccountKey=myBlobStorageKey;EndpointSuffix=core.windows.net"
export BLOB_CONTAINER_NAME="fraud-events"

# Save environment variables to a .env file (optional)
echo "Saving environment variables to .env file..."
echo "EVENT_HUB_CONNECTION_STRING=$EVENT_HUB_CONNECTION_STRING" > .env
echo "EVENT_HUB_NAME=$EVENT_HUB_NAME" >> .env
echo "BLOB_CONNECTION_STRING=$BLOB_CONNECTION_STRING" >> .env
echo "BLOB_CONTAINER_NAME=$BLOB_CONTAINER_NAME" >> .env

echo "Environment setup completed successfully."
