import os
from azure.servicebus import ServiceBusClient, ServiceBusMessage

conn_str = os.environ["SERVICE_BUS_CONNECTION_STRING"]

with ServiceBusClient.from_connection_string(conn_str) as client:
    with client.get_topic_sender("ai-jobs") as sender:
        msg = ServiceBusMessage(
            '{"file": "interview.mp4", "action": "process"}',
            content_type="application/json",
            subject="ai-job"
        )
        sender.send_messages(msg)
        print("Job sent to topic")