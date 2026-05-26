from azure.servicebus import ServiceBusClient, ServiceBusMessage

conn_str = "<insert your Service Bus connection string here>"

with ServiceBusClient.from_connection_string(conn_str) as client:
    with client.get_queue_sender("orders") as sender:
        for i in range(100):
            sender.send_messages(ServiceBusMessage(f"Order {i}"))
print("Sent 100 messages")
