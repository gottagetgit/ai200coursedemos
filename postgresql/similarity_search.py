import os
from pydoc import text
import psycopg2
from openai import AzureOpenAI

openai_client = AzureOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_KEY"],
    api_version="2024-02-01"
)

conn = psycopg2.connect(
    host=os.environ["PG_HOST"],
    database="postgres",
    user=os.environ["PG_USER"],
    password=os.environ["PG_PASSWORD"],
    sslmode="require"
)

conn.autocommit = True
cursor = conn.cursor()
cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS knowledge_base (
    id SERIAL PRIMARY KEY,
    category VARCHAR(50),
    content TEXT,
    embedding vector(1536)
    );
""")

def embed(text):
    return openai_client.embeddings.create(input=text, model="text-embedding-ada-002").data[0].embedding

# Ingest knowledge
chunks = [
    ("containers", "Azure Container Apps is a serverless platform ideal for microservices."),
    ("containers", "Azure Kubernetes Service offers full Kubernetes control for complex workloads."),
    ("databases", "Cosmos DB is a globally distributed NoSQL database with multi-model support."),
    ("databases", "PostgreSQL with pgvector enables native vector similarity search."),
]

for category, content in chunks:
    embedding = embed(content)
    cursor.execute(
        "INSERT INTO knowledge_base (category, content, embedding) VALUES (%s, %s, %s)",
        (category, content, embedding)
)

# RAG query with metadata filter
user_question = "Which Azure database supports vector search natively?"
query_embedding = embed(user_question)

cursor.execute("""
    SELECT content, embedding <=> %s::vector AS distance
    FROM knowledge_base
    WHERE category = 'databases'
    ORDER BY distance
    LIMIT 2;
""", (query_embedding,))
retrieved_chunks = cursor.fetchall()

context = "\n".join([row[0] for row in retrieved_chunks])
print("Retrieved context:\n", context)

# Generate answer
response = openai_client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": f"Answer using only this context:\n{context}"},
        {"role": "user", "content": user_question}
    ]
)
print("\nAI Answer:", response.choices[0].message.content)
