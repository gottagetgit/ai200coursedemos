import os
import uuid
import random
from azure.cosmos import CosmosClient

# Read Cosmos connection string from environment variable for safety
COSMOS_CONNECTION_STRING = os.environ["COSMOS_CONNECTION_STRING"]

# Create client from connection string
client = CosmosClient.from_connection_string(COSMOS_CONNECTION_STRING)

# Get database and container
database = client.get_database_client("ai-demo")
container = database.get_container_client("products")

# Allowed categories
CATEGORIES = ["electronics", "books", "clothing", "food"]
rucost = 0.0

def create_dynamic_product():
    global rucost
    category = random.choice(CATEGORIES)

    item = {
        "id": str(uuid.uuid4()),
        "name": f"Sample {category} item",
        "category": category,          # partition key 
        "price": round(random.uniform(5, 500), 2),
        "in_stock": random.choice([True, False])
    }

    created = container.create_item(body=item)
    rucost += float(container.client_connection.last_response_headers['x-ms-request-charge'])
    return created

if __name__ == "__main__":
    for i in range(500):
        created = create_dynamic_product()
        print(f"{i+1}/500 inserted: {created['id']} ({created['category']})")

    print(f"Total RU cost for 500 inserts: {rucost:.2f} RUs")
    print(f"Average RU per insert: {rucost / 500:.3f} RUs")
