import os
from dotenv import load_dotenv

def load_config():
    load_dotenv()
    
    config = {
        # Azure authentication
        'tenant_id': os.getenv('TENANT_ID'),
        'client_id': os.getenv('CLIENT_ID'),
        'client_secret': os.getenv('CLIENT_SECRET'),
        'subscription_id': os.getenv('SUBSCRIPTION_ID'),
        
        # Resource group
        'resource_group_name': os.getenv('RESOURCE_GROUP_NAME'),
        'location': os.getenv('LOCATION', 'eastus'),
        
        # Network
        'vnet_name': os.getenv('VNET_NAME', 'k8s-vnet'),
        'subnet_name': os.getenv('SUBNET_NAME', 'k8s-subnet'),
        
        # Head node
        'head_node_name': os.getenv('HEAD_NODE_NAME', 'k8s-master'),
        'head_node_size': os.getenv('HEAD_NODE_SIZE', 'Standard_D2s_v3'),
        
        # Worker nodes
        'worker_nodes_name': os.getenv('WORKER_NODES_NAME', 'k8s-workers'),
        'worker_node_size': os.getenv('WORKER_NODE_SIZE', 'Standard_D2s_v3'),
        'worker_node_count': int(os.getenv('WORKER_NODE_COUNT', '2')),
        
        # Authentication
        'admin_username': os.getenv('ADMIN_USERNAME', 'azureuser'),
        'admin_password': os.getenv('ADMIN_PASSWORD', 'KubeAdm1n2024!')
    }
    
    return config