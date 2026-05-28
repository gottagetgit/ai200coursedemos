import os
import time
from typing import List, Tuple

import psycopg
from openai import OpenAI
from pgvector.psycopg import register_vector

# Environment variables:
#   OPENAI_API_KEY  - your OpenAI key
#   DATABASE_URL    - postgres connection string
# Optional:
#   EMBEDDING_MODEL - defaults to text-embedding-ada-002
#   TOTAL_ROWS      - defaults to 1000
#   BATCH_SIZE      - defaults to 100
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
DATABASE_URL = os.environ["DATABASE_URL"]
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
TOTAL_ROWS = int(os.getenv("TOTAL_ROWS", "1000"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "100"))


def generate_documents(total: int) -> List[Tuple[str, str, str, int]]:
    """
    Generate (title, txtcontent, category, token_count) tuples.
    token_count is a simple length-based estimate for demo purposes.
    """
    docs: List[Tuple[str, str, str, int]] = []
    categories = ["ai", "cloud", "database", "security", "ml"]

    topics = [
        "Azure AI services",
        "vector databases",
        "retrieval augmented generation",
        "PostgreSQL and pgvector",
        "machine learning pipelines",
        "cloud security",
        "document search",
        "language models",
        "semantic indexing",
        "developer productivity",
    ]

    for i in range(1, total + 1):
        topic = topics[(i - 1) % len(topics)]
        category = categories[(i - 1) % len(categories)]

        title = f"Document {i} about {topic}"
        body = (
            f"This is document {i} in the demo dataset. "
            f"It discusses {topic} and is used to show how we generate OpenAI embeddings "
            f"and store them in PostgreSQL with pgvector for semantic search and RAG demos. "
            f"The content is intentionally similar across documents so that nearest-neighbor "
            f"queries will return related items."
        )

        # Very rough token_count estimate (word count as a stand-in)
        token_count = len(body.split())

        docs.append((title, body, category, token_count))

    return docs


def chunked(items, size: int):
    for i in range(0, len(items), size):
        yield items[i:i + size]


def main() -> None:
    client = OpenAI(api_key=OPENAI_API_KEY)
    docs = generate_documents(TOTAL_ROWS)

    with psycopg.connect(DATABASE_URL) as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            # Ensure pgvector is available (no-op if already created)
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

            # Ensure the table exists with your schema
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    title VARCHAR(255) NOT NULL,
                    txtcontent TEXT NOT NULL,
                    category VARCHAR(50),
                    embedding vector(1536),
                    token_count INTEGER,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                );
                """
            )
            conn.commit()

            inserted = 0

            for batch in chunked(docs, BATCH_SIZE):
                titles = [d[0] for d in batch]
                contents = [d[1] for d in batch]
                categories = [d[2] for d in batch]
                token_counts = [d[3] for d in batch]

                # For embeddings we usually embed the main text content
                response = client.embeddings.create(
                    model=EMBEDDING_MODEL,
                    input=contents,
                )
                vectors = [item.embedding for item in response.data]

                # Build rows matching the INSERT columns
                rows = list(
                    zip(
                        titles,
                        contents,
                        categories,
                        vectors,
                        token_counts,
                    )
                )

                cur.executemany(
                    """
                    INSERT INTO documents
                        (title, txtcontent, category, embedding, token_count)
                    VALUES
                        (%s, %s, %s, %s, %s)
                    """,
                    rows,
                )
                conn.commit()

                inserted += len(rows)
                print(f"Inserted {inserted}/{TOTAL_ROWS} rows")
                time.sleep(0.25)  # gentle pacing for the API

    print("Done seeding documents with embeddings.")


if __name__ == "__main__":
    main()
