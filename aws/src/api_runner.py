import requests

BASE_URL = "http://127.0.0.1:8000"  # Update this if the API is hosted elsewhere

def deploy_master_node():
    url = f"{BASE_URL}/deploy/master-node"
    payload = {
        "key_name": "your-key-pair",
        "instance_type": "t2.medium",
        "region": "us-east-1"
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("Master node deployed successfully!")
        print("Response:", response.json())
    else:
        print("Failed to deploy master node.")
        print("Error:", response.text)

def deploy_worker_nodes():
    url = f"{BASE_URL}/deploy/worker-nodes"
    payload = {
        "key_name": "your-key-pair",
        "instance_type": "t2.medium",
        "region": "us-east-1",
        "num_workers": 2
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("Worker nodes deployed successfully!")
        print("Response:", response.json())
    else:
        print("Failed to deploy worker nodes.")
        print("Error:", response.text)

if __name__ == "__main__":
    print("Deploying Kubernetes Master Node...")
    deploy_master_node()

    print("\nDeploying Kubernetes Worker Nodes...")
    deploy_worker_nodes()