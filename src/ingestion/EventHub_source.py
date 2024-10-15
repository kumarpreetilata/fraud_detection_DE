import os
import json
import logging
import time
from azure.eventhub import EventHubConsumerClient, EventHubError
from azure.storage.blob import BlobServiceClient, BlobServiceError
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Azure Event Hub and Blob Storage configuration
EVENT_HUB_CONNECTION_STRING = os.getenv("EVENT_HUB_CONNECTION_STRING", "Endpoint=sb://myeventhubnamespace.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=mySharedAccessKey;")
EVENT_HUB_NAME = os.getenv("EVENT_HUB_NAME", "fraudDetectionHub")
BLOB_CONNECTION_STRING = os.getenv("BLOB_CONNECTION_STRING", "DefaultEndpointsProtocol=https;AccountName=myblobstorageaccount;AccountKey=myBlobStorageKey;EndpointSuffix=core.windows.net")
BLOB_CONTAINER_NAME = os.getenv("BLOB_CONTAINER_NAME", "fraud-events")

# Create a Blob Service Client
blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)

def save_event_to_blob(event_data):
    """Save the event data to Azure Blob Storage."""
    try:
        # Convert the event data to a JSON string
        json_data = json.dumps(event_data)
        # Create a blob client for the specified container
        blob_client = blob_service_client.get_blob_client(container=BLOB_CONTAINER_NAME, blob=f"events/{event_data['transaction_id']}.json")
        
        # Upload the JSON data to the blob
        blob_client.upload_blob(json_data, overwrite=True)
        logging.info(f"Uploaded event data to blob: {event_data['transaction_id']}.json")
    except ResourceExistsError:
        logging.warning(f"Blob {event_data['transaction_id']}.json already exists. Overwriting...")
        blob_client.upload_blob(json_data, overwrite=True)
    except ResourceNotFoundError:
        logging.error(f"Blob container {BLOB_CONTAINER_NAME} not found.")
    except BlobServiceError as e:
        logging.error(f"Blob service error: {e}")
    except Exception as e:
        logging.error(f"Error saving event to blob: {e}")

def on_event(partition_context, event):
    """Event handler for processing incoming events."""
    try:
        # Deserialize the event data
        event_data = json.loads(event.body_as_str())
        logging.info(f"Received event: {event_data}")

        # Save the event data to Azure Blob Storage
        save_event_to_blob(event_data)
        
        # Checkpoint after processing the event
        partition_context.update_checkpoint(event)
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON: {e}")
    except Exception as e:
        logging.error(f"Error processing event: {e}")

def main():
    """Main function to start the Event Hub consumer."""
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
            logging.info("Listening for events...")
            # Keep the script running
            while True:
                time.sleep(1)  # Sleep to reduce CPU usage
    except KeyboardInterrupt:
        logging.info("Event processing stopped.")
    except EventHubError as e:
        logging.error(f"Event Hub error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        client.close()
        logging.info("Event Hub consumer client closed.")

if __name__ == "__main__":
    main()
