import os
import logging
import json
import pandas as pd
import joblib
from azure.storage.blob import BlobServiceClient
from azure.eventhub import EventHubConsumerClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Azure Blob Storage and Event Hub configuration
AZURE_BLOB_CONNECTION_STRING = os.getenv("AZURE_BLOB_CONNECTION_STRING")
EVENT_HUB_CONNECTION_STRING = os.getenv("EVENT_HUB_CONNECTION_STRING")
EVENT_HUB_NAME = os.getenv("EVENT_HUB_NAME")
BLOB_SERVICE_CLIENT = BlobServiceClient.from_connection_string(AZURE_BLOB_CONNECTION_STRING)
MODEL_BLOB_NAME = "fraud_detection_model.pkl"  # Name of the saved model in Blob Storage

def load_model():
    """Load the trained model from Azure Blob Storage."""
    try:
        blob_client = BLOB_SERVICE_CLIENT.get_blob_client(container="fraud-events", blob=MODEL_BLOB_NAME)
        with open(MODEL_BLOB_NAME, "wb") as model_file:
            model_file.write(blob_client.download_blob().readall())
        model = joblib.load(MODEL_BLOB_NAME)
        logger.info("Model loaded successfully.")
        return model
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        return None

def predict_event(model, event_data):
    """Make a prediction based on incoming event data."""
    try:
        # Convert event data to DataFrame
        df = pd.DataFrame([event_data])  # Convert single event data to DataFrame
        prediction = model.predict(df)
        logger.info(f"Prediction for transaction {event_data['transaction_id']}: {'Fraud' if prediction[0] else 'Not Fraud'}")
        return prediction[0]
    except Exception as e:
        logger.error(f"Error during prediction: {str(e)}")
        return None

def on_event(partition_context, event):
    """Event handler for processing incoming events."""
    try:
        # Deserialize the event data
        event_data = json.loads(event.body_as_str())
        logger.info(f"Received event: {event_data}")

        # Load the model
        model = load_model()
        if model is not None:
            # Predict if the event is fraudulent
            predict_event(model, event_data)
        
        # Checkpoint after processing the event
        partition_context.update_checkpoint(event)
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON: {e}")
    except Exception as e:
        logger.error(f"Error processing event: {e}")

def main():
    """Main function to start the Event Hub consumer for predictions."""
    # Create a consumer client for Event Hubs
    client = EventHubConsumerClient.from_connection_string(
        conn_str=EVENT_HUB_CONNECTION_STRING,
        consumer_group="$Default",
        eventhub_name=EVENT_HUB_NAME
    )

    try:
        # Start receiving events
        with client:
            client.receive(on_event=on_event, starting_position="@latest")
            logger.info("Listening for events...")
            # Keep the script running
            while True:
                pass
    except KeyboardInterrupt:
        logger.info("Event processing stopped.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        client.close()
        logger.info("Event Hub consumer client closed.")

if __name__ == "__main__":
    main()
