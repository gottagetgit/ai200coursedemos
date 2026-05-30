import os
import numpy as np
from openai import AzureOpenAI
from redis import Redis
from redis.commands.search.field import TextField, VectorField
from redis.commands.search.index_definition import IndexDefinition, IndexType
from redis.exceptions import ResponseError

INDEX_NAME = "idx:prompts"
KEY_PREFIX = "prompt:"
REDIS_PORT = 10000
EMBEDDING_MODEL = "text-embedding-ada-002"

openai_client = AzureOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_KEY"],
    api_version="2024-02-01",
)

redis_client = Redis(
    host=os.environ["REDIS_HOST"],
    port=REDIS_PORT,
    password=os.environ["REDIS_KEY"],
    ssl=True,
    decode_responses=False,
)


def get_embedding(text: str) -> list[float]:
    response = openai_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
    )
    return response.data[0].embedding


def create_index(vector_dim: int) -> None:
    schema = (
        TextField("prompt"),
        TextField("response"),
        VectorField(
            "embedding",
            "HNSW",
            {
                "TYPE": "FLOAT32",
                "DIM": vector_dim,
                "DISTANCE_METRIC": "COSINE",
                "M": 16,
                "EF_CONSTRUCTION": 200,
            },
        ),
    )

    try:
        redis_client.ft(INDEX_NAME).dropindex(delete_documents=True)
    except ResponseError:
        pass

    redis_client.ft(INDEX_NAME).create_index(
        schema,
        definition=IndexDefinition(
            prefix=[KEY_PREFIX],
            index_type=IndexType.HASH,
        ),
    )


def store_document(doc_id: int, prompt: str, response: str) -> None:
    embedding = np.array(get_embedding(prompt), dtype=np.float32).tobytes()
    key = f"{KEY_PREFIX}{doc_id}"
    redis_client.hset(key, "prompt", prompt)
    redis_client.hset(key, "response", response)
    redis_client.hset(key, "embedding", embedding)


def semantic_search(query_text: str, top_k: int = 2):
    query_vector = np.array(get_embedding(query_text), dtype=np.float32).tobytes()

    result = redis_client.execute_command(
        "FT.SEARCH",
        INDEX_NAME,
        f"(*)=>[KNN {top_k} @embedding $vec AS score]",
        "PARAMS", "2", "vec", query_vector,
        "SORTBY", "score",
        "RETURN", "3", "prompt", "response", "score",
        "DIALECT", "2",
    )

    return result


def print_results(raw_result) -> None:
    print(f"Total results: {raw_result[b'total_results']}")
    print()

    for i, item in enumerate(raw_result[b"results"], start=1):
        fields = item[b"extra_attributes"]
        prompt = fields[b"prompt"].decode("utf-8")
        response = fields[b"response"].decode("utf-8")
        score = fields[b"score"].decode("utf-8")

        print(f"Rank {i}")
        print(f"Score   : {score}")
        print(f"Prompt  : {prompt}")
        print(f"Response: {response}")
        print()


def main():
    sample_docs = [
        (
            "What is Azure Container Apps?",
            "Azure Container Apps is a serverless platform for running containerized applications without managing Kubernetes or infrastructure."
        ),
        (
            "What is Azure Kubernetes Service?",
            "Azure Kubernetes Service is a managed Kubernetes platform for deploying, scaling, and operating containerized workloads."
        ),
        (
            "What is Azure Container Instances?",
            "Azure Container Instances lets you run containers on demand in Azure without managing virtual machines or an orchestrator."
        ),
        (
            "What is Azure Container Registry?",
            "Azure Container Registry is a private registry for storing and managing container images and OCI artifacts."
        ),
        (
            "What is Azure App Service for Containers?",
            "Azure App Service for Containers lets you run containerized web applications on the Azure App Service platform."
        ),
        (
            "What is Azure Functions?",
            "Azure Functions is a serverless compute service that runs event-driven code without requiring you to manage servers."
        ),
        (
            "What is Azure Virtual Machines?",
            "Azure Virtual Machines provides on-demand scalable Windows and Linux virtual machines in Azure."
        ),
        (
            "What is Azure Service Bus?",
            "Azure Service Bus is a fully managed enterprise message broker used for reliable messaging between applications and services."
        ),
        (
            "What is Azure API Management?",
            "Azure API Management helps organizations publish, secure, transform, monitor, and manage APIs."
        ),
    ]

    vector_dim = len(get_embedding("test"))
    create_index(vector_dim)

    for i, (prompt, response) in enumerate(sample_docs, start=1):
        store_document(i, prompt, response)

    query = "Tell me about Container Apps on Azure"
    results = semantic_search(query, top_k=2)

    print(f"Query: {query}")
    print()
    print_results(results)


if __name__ == "__main__":
    main()
