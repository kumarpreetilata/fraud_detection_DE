import os
import json
import logging
import joblib
from flask import Flask, request, jsonify
from azure.storage.blob import BlobServiceClient
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Azure Blob Storage configuration
AZURE_BLOB_CONNECTION_STRING = os.getenv("AZURE_BLOB_CONNECTION_STRING")
BLOB_CONTAINER_NAME = "fraud-events"  # Name of the blob container
MODEL_BLOB_NAME = "fraud_detection_model.pkl"  # Name of the saved model in Blob Storage

# Initialize Flask app
app = Flask(__name__)

def load_model_from_blob():
    """Load the trained model from Azure Blob Storage."""
    try:
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_BLOB_CONNECTION_STRING)
        blob_client = blob_service_client.get_blob_client(container=BLOB_CONTAINER_NAME, blob=MODEL_BLOB_NAME)

        # Download the model blob
        with open(MODEL_BLOB_NAME, "wb") as model_file:
            model_data = blob_client.download_blob()
            model_data.readinto(model_file)

        # Load the model using joblib
        model = joblib.load(MODEL_BLOB_NAME)
        logger.info("Model loaded successfully from Azure Blob Storage.")
        return model
    except Exception as e:
        logger.error(f"Failed to load model from blob: {str(e)}")
        return None

# Load the model on startup
model = load_model_from_blob()

@app.route('/predict', methods=['POST'])
def predict():
    """Endpoint to make predictions on transaction data."""
    try:
        # Get JSON data from the request
        data = request.get_json()

        # Convert the JSON data to a DataFrame
        transaction_data = pd.DataFrame([data])

        # Make prediction
        prediction = model.predict(transaction_data)
        result = {
            "transaction_id": data.get("transaction_id"),
            "is_fraud": int(prediction[0])  # Convert to integer for easier readability
        }

        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({"error": "Failed to process the request."}), 400

if __name__ == "__main__":
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000)
