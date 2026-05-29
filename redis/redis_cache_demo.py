import os, json, hashlib
import redis
from openai import AzureOpenAI

r = redis.Redis(
    host=os.environ["REDIS_HOST"],
    port=6380,
    password=os.environ["REDIS_KEY"],
    ssl=True
)
openai_client = AzureOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_KEY"],
    api_version="2024-02-01"
)
def get_cached_response(prompt, ttl=3600):
    cache_key = "llm:" + hashlib.md5(prompt.encode()).hexdigest()
    cached = r.get(cache_key)
    if cached:
        print("CACHE HIT")
        return json.loads(cached)
    
    print("CACHE MISS - calling OpenAI")
    response = openai_client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}]
    )
    result = response.choices[0].message.content
    r.setex(cache_key, ttl, json.dumps(result)) # Cache for 1 hour
    return result

# First call - cache miss
print(get_cached_response("What is Azure Container Apps?"))
# Second call - cache hit
print(get_cached_response("What is Azure Container Apps?"))
