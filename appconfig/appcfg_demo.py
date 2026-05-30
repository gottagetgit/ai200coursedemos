import os
from azure.appconfiguration import AzureAppConfigurationClient
from azure.identity import DefaultAzureCredential

endpoint = "https://appcfg-ai-demo.azconfig.io"
client = AzureAppConfigurationClient(endpoint, DefaultAzureCredential())

# Read a single setting
model_name = client.get_configuration_setting(key="AI:ModelName")
print(f"Model: {model_name.value}")

# Read with a label (environment override)
dev_model = client.get_configuration_setting(key="AI:ModelName", label="dev")
print(f"Dev Model: {dev_model.value}")

# List all settings
settings = client.list_configuration_settings()
for s in settings:
    print(f"{s.key}: {s.value}")

