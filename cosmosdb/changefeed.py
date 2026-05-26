import asyncio
from azure.cosmos.aio import CosmosClient
from azure.cosmos import PartitionKey

# Read Cosmos connection string from environment variable
COSMOS_CONNECTION_STRING = os.environ["COSMOS_CONNECTION_STRING"]

async def handle_changes(changes, context):
    for change in changes:
    print(f"Change detected: {change['id']} - {change.get('name', 'no name')}")

async def main():
    async with CosmosClient.from_connection_string(COSMOS_CONNECTION_STRING) as client:
    db = client.get_database_client("ai-demo")
    monitored = db.get_container_client("products")
    leases = db.get_container_client("leases")
    processor = monitored.get_change_feed_processor(
        processor_name="demo-processor",
        lease_container=leases,
        on_change=handle_changes
    )
    await processor.start()
    print("Listening for changes - add or update items in the portal...")
    await asyncio.sleep(60) # Run for 60 seconds
    await processor.stop()

asyncio.run(main())
