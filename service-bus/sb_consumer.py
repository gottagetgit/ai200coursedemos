import os
from azure.servicebus import ServiceBusClient
import random

conn_str = os.environ["SERVICE_BUS_CONNECTION_STRING"]

with ServiceBusClient.from_connection_string(conn_str) as client:
    with client.get_subscription_receiver("ai-jobs", "transcription-sub", max_wait_time=5) as receiver:
        for msg in receiver:
            try:
                print(f"Received: {str(msg)}")
                # Simulate a processing failure
                if random.random() < 0.3:
                    raise ValueError("Transcription service unavailable")
                receiver.complete_message(msg)
            except Exception as e:
                print(f"Failed: {e} - dead lettering message")
                receiver.dead_letter_message(
                    msg,
                    reason="ProcessingFailed",
                    error_description=str(e),
                )
