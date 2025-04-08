import requests
import os
from dotenv import load_dotenv
import argparse

# Load environment variables
load_dotenv()

# Base URL for API
BASE_URL = os.environ.get("API_BASE_URL", "http://127.0.0.1:8000")

def deploy_cluster(provider="azure"):
    """Deploy a complete Kubernetes cluster on the specified cloud provider"""
    if provider.lower() == "azure":
        head_node_response = deploy_azure_head_node()
        if head_node_response:
            join_token = input("\nEnter the Kubernetes join token from the head node: ").strip()
            deploy_azure_worker_nodes(join_token)
    elif provider.lower() == "aws":
        deploy_aws_master_node()
        deploy_aws_worker_nodes()
    else:
        print(f"Unsupported provider: {provider}")

def deploy_azure_head_node():
    """Deploy a Kubernetes head node on Azure"""
    print("\n=== Deploying Azure Kubernetes Head Node ===")
    
    url = f"{BASE_URL}/deploy/head-node"
    payload = {
        "provider": "azure",
        "cluster_name": os.environ.get("AZURE_HEAD_NODE_NAME", "k8s-master"),
        "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP", "k8s-resource-group"),
        "region": os.environ.get("AZURE_LOCATION", "eastus"),
        "node_size": os.environ.get("AZURE_HEAD_NODE_SIZE", "Standard_D2s_v3"),
        "vnet_name": os.environ.get("AZURE_VNET_NAME", "k8s-vnet"),
        "subnet_name": os.environ.get("AZURE_SUBNET_NAME", "k8s-subnet"),
        "admin_username": os.environ.get("AZURE_ADMIN_USERNAME", "azureuser"),
        "admin_password": os.environ.get("AZURE_ADMIN_PASSWORD", "KubeAdm1n2024!")
    }
    
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("✅ Head node deployed successfully!")
        print("Response:", response.json())
        return True
    else:
        print("❌ Failed to deploy head node.")
        print("Error:", response.text)
        return False

def deploy_azure_worker_nodes(join_token):
    """Deploy Kubernetes worker nodes on Azure"""
    print("\n=== Deploying Azure Kubernetes Worker Nodes ===")
    
    url = f"{BASE_URL}/deploy/worker-nodes"
    payload = {
        "provider": "azure",
        "cluster_name": os.environ.get("AZURE_WORKER_NODES_NAME", "k8s-workers"),
        "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP", "k8s-resource-group"),
        "region": os.environ.get("AZURE_LOCATION", "eastus"),
        "node_size": os.environ.get("AZURE_WORKER_NODE_SIZE", "Standard_D2s_v3"),
        "worker_count": int(os.environ.get("AZURE_WORKER_NODE_COUNT", "2")),
        "vnet_name": os.environ.get("AZURE_VNET_NAME", "k8s-vnet"),
        "subnet_name": os.environ.get("AZURE_SUBNET_NAME", "k8s-subnet"),
        "join_token": join_token,
        "admin_username": os.environ.get("AZURE_ADMIN_USERNAME", "azureuser"),
        "admin_password": os.environ.get("AZURE_ADMIN_PASSWORD", "KubeAdm1n2024!")
    }
    
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("✅ Worker nodes deployed successfully!")
        print("Response:", response.json())
        return True
    else:
        print("❌ Failed to deploy worker nodes.")
        print("Error:", response.text)
        return False

def deploy_aws_master_node():
    """Deploy a Kubernetes master node on AWS"""
    print("\n=== Deploying AWS Kubernetes Master Node ===")
    
    url = f"{BASE_URL}/deploy/head-node"
    payload = {
        "provider": "aws",
        "cluster_name": os.environ.get("AWS_CLUSTER_NAME", "k8s-cluster"),
        "region": os.environ.get("AWS_REGION", "us-east-1"),
        "node_size": os.environ.get("AWS_INSTANCE_TYPE", "t2.medium"),
        "ssh_key_name": os.environ.get("AWS_KEY_NAME", "your-key-pair")
    }
    
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("✅ Master node deployed successfully!")
        print("Response:", response.json())
        return True
    else:
        print("❌ Failed to deploy master node.")
        print("Error:", response.text)
        return False

def deploy_aws_worker_nodes():
    """Deploy Kubernetes worker nodes on AWS"""
    print("\n=== Deploying AWS Kubernetes Worker Nodes ===")
    
    url = f"{BASE_URL}/deploy/worker-nodes"
    payload = {
        "provider": "aws",
        "cluster_name": os.environ.get("AWS_CLUSTER_NAME", "k8s-cluster"),
        "region": os.environ.get("AWS_REGION", "us-east-1"),
        "node_size": os.environ.get("AWS_INSTANCE_TYPE", "t2.medium"),
        "ssh_key_name": os.environ.get("AWS_KEY_NAME", "your-key-pair"),
        "worker_count": int(os.environ.get("AWS_WORKER_COUNT", "2"))
    }
    
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("✅ Worker nodes deployed successfully!")
        print("Response:", response.json())
        return True
    else:
        print("❌ Failed to deploy worker nodes.")
        print("Error:", response.text)
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploy Kubernetes clusters on cloud providers")
    parser.add_argument(
        "--provider", 
        type=str, 
        default=os.environ.get("CLOUD_PROVIDER", "azure"),
        choices=["azure", "aws"],
        help="Cloud provider to use (azure or aws)"
    )
    args = parser.parse_args()
    
    print(f"=== Kubernetes Deployment on {args.provider.upper()} ===")
    deploy_cluster(args.provider)