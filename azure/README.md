# Azure Kubernetes Deployment Project

This project demonstrates how to deploy a Kubernetes cluster on Azure using the Azure Python SDK. It includes functionality to deploy a Kubernetes head node and worker nodes using Virtual Machines and Virtual Machine Scale Sets (VMSS).

## Project Structure

```
azure
├── src
│   ├── api
│   │   └── main.py                 # FastAPI implementation for Azure
│   ├── head_node.py                # Logic for deploying the Kubernetes head node
│   ├── worker_nodes.py             # Logic for deploying Kubernetes worker nodes
│   ├── kubernetes_deployer.py      # Base class for Kubernetes deployment
│   ├── templates
│   │   ├── cloud_init_head_node.yaml  # Cloud-init template for head node
│   │   └── cloud_init_worker_node.yaml # Cloud-init template for worker nodes
│   └── utils
│       └── azure_helpers.py        # Azure utility functions
├── tests
│   ├── test_api.py                 # Unit tests for the API
│   └── test_worker_nodes.py        # Unit tests for worker node deployment
├── azure_config.py                 # Configuration settings for Azure resources
├── requirements.txt                # Project dependencies
├── .env                            # Environment variables
└── README.md                       # Project documentation
```

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd azure
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Create a `.env` file in the root directory and add your Azure credentials and other necessary configurations. Example:

   ```
   AZURE_TENANT_ID=<your-tenant-id>
   AZURE_CLIENT_ID=<your-client-id>
   AZURE_CLIENT_SECRET=<your-client-secret>
   AZURE_SUBSCRIPTION_ID=<your-subscription-id>
   ```

## Environment Variables

The following environment variables are required for the project:

### Azure Authentication
- `AZURE_TENANT_ID`: Your Azure tenant ID.
- `AZURE_CLIENT_ID`: Your Azure client ID.
- `AZURE_CLIENT_SECRET`: Your Azure client secret.
- `AZURE_SUBSCRIPTION_ID`: Your Azure subscription ID.

### Resource Group
- `RESOURCE_GROUP_NAME`: The name of the Azure resource group to use or create.
- `LOCATION`: The Azure region where resources will be deployed (e.g., `eastus`).

### Network
- `VNET_NAME`: The name of the virtual network.
- `SUBNET_NAME`: The name of the subnet within the virtual network.

### Head Node
- `HEAD_NODE_NAME`: The name of the Kubernetes head node.
- `HEAD_NODE_SIZE`: The size of the virtual machine for the head node (e.g., `Standard_D2s_v3`).

### Worker Nodes
- `WORKER_NODES_NAME`: The name of the Kubernetes worker nodes.
- `WORKER_NODE_SIZE`: The size of the virtual machines for the worker nodes (e.g., `Standard_D2s_v3`).
- `WORKER_NODE_COUNT`: The number of worker nodes to deploy.

### Authentication
- `ADMIN_USERNAME`: The administrator username for the virtual machines.
- `ADMIN_PASSWORD`: The administrator password for the virtual machines.

## Usage

### Deploy Kubernetes Head Node

To deploy the Kubernetes head node, run the following command:

```bash
python src/head_node.py
```

### Deploy Kubernetes Worker Nodes

To deploy the Kubernetes worker nodes, run the following command:

```bash
python src/worker_nodes.py
```

Make sure to update the configuration settings in `azure_config.py` as needed.

## Running Tests

To run the unit tests, execute:

```bash
pytest tests/
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License.