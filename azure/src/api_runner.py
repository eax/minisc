import requests

BASE_URL = "http://127.0.0.1:8000"  # Update this if the API is hosted elsewhere

def deploy_head_node():
    url = f"{BASE_URL}/deploy/head-node"
    payload = {
        "resource_group_name": "k8s-resource-group",
        "head_node_name": "k8s-master",
        "location": "eastus",
        "head_node_size": "Standard_D2s_v3",
        "vnet_name": "k8s-vnet",
        "subnet_name": "k8s-subnet",
        "admin_username": "azureuser",
        "admin_password": "KubeAdm1n2024!"
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("Head node deployed successfully!")
        print("Response:", response.json())
    else:
        print("Failed to deploy head node.")
        print("Error:", response.text)

def deploy_worker_nodes(join_token):
    url = f"{BASE_URL}/deploy/worker-nodes"
    payload = {
        "resource_group_name": "k8s-resource-group",
        "vmss_name": "k8s-workers",
        "location": "eastus",
        "worker_node_size": "Standard_D2s_v3",
        "worker_node_count": 2,
        "vnet_name": "k8s-vnet",
        "subnet_name": "k8s-subnet",
        "join_token": join_token,
        "admin_username": "azureuser",
        "admin_password": "KubeAdm1n2024!"
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("Worker nodes deployed successfully!")
        print("Response:", response.json())
    else:
        print("Failed to deploy worker nodes.")
        print("Error:", response.text)

if __name__ == "__main__":
    print("Deploying Kubernetes Head Node...")
    deploy_head_node()

    print("\nOnce the head node is deployed, retrieve the join token from the head node.")
    join_token = input("Enter the Kubernetes join token: ").strip()

    print("\nDeploying Kubernetes Worker Nodes...")
    deploy_worker_nodes(join_token)