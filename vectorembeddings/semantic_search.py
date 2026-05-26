import os
from openai import AzureOpenAI
from azure.cosmos import CosmosClient

# Clients
openai_client = AzureOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_KEY"],
    api_version="2024-02-01"
)

conn_str = os.environ["COSMOS_CONNECTION_STRING"]
cosmos_client = CosmosClient.from_connection_string(conn_str)
container = cosmos_client.get_database_client("ai-demo").get_container_client("documents")

def get_embedding(text):
    response = openai_client.embeddings.create(input=text, model="text-embedding-ada-002")
    return response.data[0].embedding

# Store documents with embeddings
docs = [
    "Azure Container Apps is a serverless platform for microservices.", 
    "Azure Kubernetes Service provides managed Kubernetes clusters.",
    "Cosmos DB is a globally distributed NoSQL database."
]

for i, doc in enumerate(docs):
    embedding = get_embedding(doc)
    container.upsert_item({"id": str(i), "text": doc, "embedding": embedding})
    print(f"Stored doc {i}")

# Search
query = "What service runs containers without managing servers?"
query_embedding = get_embedding(query)

results = container.query_items(
    query="""SELECT TOP 2 c.text, VectorDistance(c.embedding, @qe) AS score
    FROM c ORDER BY VectorDistance(c.embedding, @qe)""",
    parameters=[{"name": "@qe", "value": query_embedding}],
    enable_cross_partition_query=True
)

for r in results:
    print(f"Score: {r['score']:.4f} | {r['text']}")
