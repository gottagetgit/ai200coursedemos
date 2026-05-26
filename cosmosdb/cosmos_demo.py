import os
from azure.cosmos import CosmosClient

# Recommended: load from environment variable
conn_str = os.environ["COSMOS_CONNECTION_STRING"]

client = CosmosClient.from_connection_string(conn_str)

database = client.get_database_client("ai-demo")
container = database.get_container_client("products")

# Query all electronics
query = "SELECT * FROM c WHERE c.category = 'electronics'"
items = list(container.query_items(query=query, enable_cross_partition_query=True))

#query = "SELECT * FROM c WHERE c.price < @maxprice"
#params = [{"name": "@maxprice", "value": 700}]
#items = list(container.query_items(query=query, parameters=params, enable_cross_partition_query=False))

for item in items:
    print(item)

print (f"RU Cost: {container.client_connection.last_response_headers['x-ms-request-charge']}")
