from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource.resources.models import ResourceGroup

class KubernetesDeployer:
    def __init__(self, tenant_id, client_id, client_secret, subscription_id):
        self.credential = ClientSecretCredential(tenant_id, client_id, client_secret)
        self.subscription_id = subscription_id
        self.resource_client = ResourceManagementClient(self.credential, subscription_id)
        self.compute_client = ComputeManagementClient(self.credential, subscription_id)
        self.network_client = NetworkManagementClient(self.credential, subscription_id)

    def create_resource_group(self, group_name, location):
        resource_group_params = ResourceGroup(location=location)
        self.resource_client.resource_groups.create_or_update(group_name, resource_group_params)
        print(f"Resource group '{group_name}' created or updated.")

    def _ensure_network_exists(self, group_name, location, vnet_name, subnet_name):
        # Check if VNet exists, create if not
        try:
            vnet = self.network_client.virtual_networks.get(group_name, vnet_name)
            print(f"Using existing virtual network '{vnet_name}'.")
        except:
            vnet = self.network_client.virtual_networks.begin_create_or_update(
                group_name,
                vnet_name,
                {
                    "location": location,
                    "address_space": {
                        "address_prefixes": ["10.0.0.0/16"]
                    }
                }
            ).result()
            print(f"Created virtual network '{vnet_name}'.")
        
        # Check if subnet exists, create if not
        try:
            subnet = self.network_client.subnets.get(group_name, vnet_name, subnet_name)
            print(f"Using existing subnet '{subnet_name}'.")
        except:
            subnet = self.network_client.subnets.begin_create_or_update(
                group_name,
                vnet_name,
                subnet_name,
                {"address_prefix": "10.0.0.0/24"}
            ).result()
            print(f"Created subnet '{subnet_name}'.")