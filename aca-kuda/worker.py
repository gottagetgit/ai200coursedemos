import os
import time

from azure.servicebus import ServiceBusClient

conn_str = os.environ["SERVICE_BUS_CONNECTION_STRING"]
queue_name = "orders"

with ServiceBusClient.from_connection_string(conn_str) as client:
	with client.get_queue_receiver(queue_name) as receiver:
		while True:
			messages = receiver.receive_messages(max_message_count=1, max_wait_time=5)
			for msg in messages:
				print(f"Processing: {str(msg)}")
				time.sleep(2)  # Simulate work
				receiver.complete_message(msg)
