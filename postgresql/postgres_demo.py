import os
import psycopg2

conn = psycopg2.connect(
    host=os.environ.get("POSTGRES_DB_HOST"),
    database="postgres",
    user=os.environ.get("POSTGRES_ADMIN"),
    password=os.environ.get("POSTGRES_PASSWORD"),
    sslmode="require"
)
cursor = conn.cursor()
cursor.execute("SELECT version();")
print(cursor.fetchone())

cursor.execute("""
    CREATE TABLE IF NOT EXISTS ai_documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
    );
""")
conn.commit()

cursor.execute("INSERT INTO ai_documents (content) VALUES (%s)", ("Azure is great for AI!",))
conn.commit()

cursor.execute("SELECT * FROM ai_documents;")
for row in cursor.fetchall():
    print(row)

cursor.close()
conn.close()