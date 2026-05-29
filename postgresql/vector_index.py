import os
import time

import psycopg
from openai import OpenAI
from pgvector.psycopg import register_vector

# Environment variables:
#   OPENAI_API_KEY  - your OpenAI key
#   DATABASE_URL    - Postgres connection string
# Optional:
#   EMBEDDING_MODEL - defaults to text-embedding-ada-002
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
DATABASE_URL = os.environ["DATABASE_URL"]
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")


def get_query_embedding(client: OpenAI, query_text: str):
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=[query_text],
    )
    # Take the first embedding from the batch
    return response.data[0].embedding


def main():
    client = OpenAI(api_key=OPENAI_API_KEY)
    query_text = "documents about vector search in PostgreSQL"

    print(f"Generating embedding for query: {query_text!r}")
    query_embedding = get_query_embedding(client, query_text)

    # Connect to Postgres
    with psycopg.connect(DATABASE_URL) as conn:
        register_vector(conn)

        with conn.cursor() as cursor:
            start = time.time()

            cursor.execute(
                """
                SELECT
                    title,
                    embedding <=> %s::vector AS distance
                FROM documents
                ORDER BY distance
                LIMIT 5;
                """,
                (query_embedding,),
            )

            results = cursor.fetchall()
            elapsed = time.time() - start

    print(f"\nBrute force time: {elapsed:.3f}s\n")
    print("Top 5 most similar documents:")
    for title, distance in results:
        print(f"- {title}  (distance = {distance:.4f})")


if __name__ == "__main__":
    main()
