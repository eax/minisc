# Import the needed credential and management objects from the libraries.
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
import os
from dotenv import load_dotenv

print("Loading environment variables from .env file")
load_dotenv(".env")



# Acquire a credential object.
credential = DefaultAzureCredential()

# Retrieve subscription ID from environment variable.
subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]

# Obtain the management object for resources.
resource_client = ResourceManagementClient(credential, subscription_id)

# Retrieve the list of resource groups
group_list = resource_client.resource_groups.list()

# Show the groups in formatted output
column_width = 40

print("Resource Group".ljust(column_width) + "Location")
print("-" * (column_width * 2))

for group in list(group_list):
    print(f"{group.name:<{column_width}}{group.location}")