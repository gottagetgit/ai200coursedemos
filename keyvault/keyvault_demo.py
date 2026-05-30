import os
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

vault_url = f"https://azsjdkv.vault.azure.net/"
credential = DefaultAzureCredential()
client = SecretClient(vault_url=vault_url, credential=credential)

# Retrieve the secret
secret = client.get_secret("open-ai-key")
print(f"Retrieved secret: {secret.value[:10]}...") # Never print full value in production!

# List all secret versions
versions = client.list_properties_of_secret_versions("open-ai-key")
for v in versions:
    print(f"Version: {v.id}, Created: {v.created_on}, Enabled: {v.enabled}")
