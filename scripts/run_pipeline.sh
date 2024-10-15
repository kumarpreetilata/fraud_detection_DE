#!/bin/bash

# Set up environment variables if needed
export EVENT_HUB_CONNECTION_STRING="Endpoint=sb://myeventhubnamespace.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=mySharedAccessKey;"
export EVENT_HUB_NAME="fraudDetectionHub"
export BLOB_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=myblobstorageaccount;AccountKey=myBlobStorageKey;EndpointSuffix=core.windows.net"
export BLOB_CONTAINER_NAME="fraud-events"

# Function to run ingestion scripts
run_ingestion() {
    echo "Running data ingestion..."
    python ingestion/data_ingestion.py
}

# Function to run data processing
run_processing() {
    echo "Running data processing..."
    python data_processing.py
}

# Function to run feature engineering
run_feature_engineering() {
    echo "Running feature engineering..."
    python feature_engineering.py
}

# Function to run model training
run_model_training() {
    echo "Running model training..."
    python modeling/train_model.py
}

# Function to run predictions
run_predictions() {
    echo "Running predictions..."
    python predict.py
}

# Function to run API integration
run_api_integration() {
    echo "Running API integration..."
    python api_integration.py
}

# Function to run deployment
run_deployment() {
    echo "Deploying model..."
    python deployment/deploy_model.py
}

# Function to run testing
run_testing() {
    echo "Running tests..."
    pytest test_ingestion.py
    pytest test_processing.py
    pytest test_modelling.py
    pytest test_deployment.py
}

# Function to run notebooks
run_notebooks() {
    echo "Running notebooks..."
    jupyter nbconvert --to notebook --execute notebooks/data_exploration.ipynb
    jupyter nbconvert --to notebook --execute notebooks/data_processing.ipynb
    jupyter nbconvert --to notebook --execute notebooks/model_evaluation.ipynb
    jupyter nbconvert --to notebook --execute notebooks/model_training.ipynb
}

# Execute pipeline steps
run_ingestion
run_processing
run_feature_engineering
run_model_training
run_predictions
run_api_integration
run_deployment
run_testing
run_notebooks

echo "Pipeline execution completed successfully."
