# Multi-Cloud Kubernetes Deployment Project

This project demonstrates how to deploy Kubernetes clusters across multiple cloud providers (Azure and AWS) using cloud provider SDKs. It includes functionality to deploy Kubernetes head/master nodes and worker nodes through a unified API interface.

## Project Structure

```
minisc/
├── api/
│   └── main.py                    # Unified FastAPI implementation for both clouds
├── azure/
│   ├── __init__.py
│   ├── config.py                  # Configuration loader for Azure
│   ├── head_node.py               # Logic for deploying Azure Kubernetes head node
│   ├── kubernetes_deployer.py     # Base class for Azure Kubernetes deployment
│   ├── main.py                    # Azure-specific CLI runner
│   └── worker_nodes.py            # Logic for deploying Azure worker nodes
├── aws/
│   ├── __init__.py
│   ├── kubernetes_deployer.py     # Base class for AWS infrastructure
│   ├── main.py                    # AWS-specific CLI runner
│   ├── main_old.py                # Legacy AWS implementation
│   ├── master_node_deployer.py    # Logic for deploying AWS master node
│   └── worker_nodes_deployer.py   # Logic for deploying AWS worker nodes
├── common/
│   ├── models.py                  # Shared data models for API requests
│   └── provider_factory.py        # Factory for creating cloud provider instances
├── templates/
│   ├── cloud-init_head_node.yaml  # Cloud-init template for head node
│   └── cloud-init_worker_node.yaml # Cloud-init template for worker nodes
├── scripts/
│   ├── master_init.sh             # Bootstrap script for AWS master configuration
│   ├── worker_init.sh             # Bootstrap script for AWS worker configuration
│   └── ubuntu/                    # Ubuntu-specific scripts
│       ├── master_init.sh         # Ubuntu master initialization script
│       └── worker_init.sh         # Ubuntu worker initialization script
├── tests/
│   ├── test_aws_api.py            # Tests for AWS API endpoints
│   └── test_azure_api.py          # Tests for Azure API endpoints
├── main.py                        # Combined CLI runner for both clouds
├── api_runner.py                  # Client script for interacting with the API
├── startapi.sh                    # Helper script to start the unified API server
├── Pipfile                        # Python dependencies using pipenv
├── requirements.txt               # Python dependencies in standard format
├── .env                           # Environment variables
└── README.md                      # Project documentation
```

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd minisc
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
   Create a `.env` file in the root directory and add your cloud provider credentials and other necessary configurations. Example:

   ```
   # Common settings
   CLOUD_PROVIDER=azure  # or aws

   # Azure settings
   AZURE_TENANT_ID=<your-tenant-id>
   AZURE_CLIENT_ID=<your-client-id>
   AZURE_CLIENT_SECRET=<your-client-secret>
   AZURE_SUBSCRIPTION_ID=<your-subscription-id>
   RESOURCE_GROUP_NAME=k8s-resource-group
   LOCATION=eastus
   VNET_NAME=k8s-vnet
   SUBNET_NAME=k8s-subnet
   HEAD_NODE_NAME=k8s-master
   HEAD_NODE_SIZE=Standard_D2s_v3
   WORKER_NODES_NAME=k8s-workers
   WORKER_NODE_SIZE=Standard_D2s_v3
   WORKER_NODE_COUNT=2
   ADMIN_USERNAME=azureuser
   ADMIN_PASSWORD=<your-secure-password>

   # AWS settings
   AWS_REGION=us-east-1
   AWS_ACCESS_KEY_ID=<your-access-key-id>
   AWS_SECRET_ACCESS_KEY=<your-secret-access-key>
   AWS_KEY_NAME=your-key-pair
   AWS_INSTANCE_TYPE=t2.medium
   AWS_WORKER_COUNT=2
   ```

## Environment Variables

The following environment variables are required for the project:

### Common Settings
- `CLOUD_PROVIDER`: Specify the cloud provider (`azure` or `aws`).

### Azure Authentication
- `AZURE_TENANT_ID`: Your Azure tenant ID.
- `AZURE_CLIENT_ID`: Your Azure client ID.
- `AZURE_CLIENT_SECRET`: Your Azure client secret.
- `AZURE_SUBSCRIPTION_ID`: Your Azure subscription ID.

### Azure Resource Group
- `RESOURCE_GROUP_NAME`: The name of the Azure resource group to use or create.
- `LOCATION`: The Azure region where resources will be deployed (e.g., `eastus`).

### Azure Network
- `VNET_NAME`: The name of the virtual network.
- `SUBNET_NAME`: The name of the subnet within the virtual network.

### Azure Head/Master Node
- `HEAD_NODE_NAME`: The name of the Kubernetes head/master node.
- `HEAD_NODE_SIZE`: The size of the virtual machine for the head/master node (e.g., `Standard_D2s_v3`).

### Azure Worker Nodes
- `WORKER_NODES_NAME`: The name of the Kubernetes worker nodes.
- `WORKER_NODE_SIZE`: The size of the virtual machines for the worker nodes (e.g., `Standard_D2s_v3`).
- `WORKER_NODE_COUNT`: The number of worker nodes to deploy.

### Azure Authentication
- `ADMIN_USERNAME`: The administrator username for the virtual machines.
- `ADMIN_PASSWORD`: The administrator password for the virtual machines.

### AWS Authentication
- `AWS_ACCESS_KEY_ID`: Your AWS access key ID.
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret access key.

### AWS Settings
- `AWS_REGION`: The AWS region where resources will be deployed (e.g., `us-east-1`).
- `AWS_KEY_NAME`: The name of the key pair for AWS instances.
- `AWS_INSTANCE_TYPE`: The instance type for AWS virtual machines (e.g., `t2.medium`).
- `AWS_WORKER_COUNT`: The number of worker nodes to deploy.

## Usage

### Deploy Kubernetes Head/Master Node

To deploy the Kubernetes head/master node, run the following command:

```bash
python azure/head_node.py
```

### Deploy Kubernetes Worker Nodes

To deploy the Kubernetes worker nodes, run the following command:

```bash
python azure/worker_nodes.py
```

Make sure to update the configuration settings in `azure/config.py` or `aws/main.py` as needed.

## Testing

The project includes a comprehensive test suite that covers both cloud providers, the unified API, and common components.

### Test Structure

Tests are organized into several categories:
- API tests (`tests/test_unified_api.py`, `tests/test_aws_api.py`, `tests/test_azure_api.py`)
- Provider-specific tests (in `azure/tests/` and `aws/tests/`) 
- Common component tests (`tests/test_provider_factory.py`, `tests/test_models.py`)

### Running Tests

#### Running All Tests

To run the entire test suite:

```bash
pytest
```

#### Running Specific Tests

To run a specific test file, use the following command:

```bash
pytest <path-to-test-file>
```

For example:
- To run tests for the unified API:
  ```bash
  pytest tests/test_unified_api.py
  ```
- To run tests for AWS API endpoints:
  ```bash
  pytest tests/test_aws_api.py
  ```
- To run tests for Azure API endpoints:
  ```bash
  pytest tests/test_azure_api.py
  ```

To run a specific test function within a file, use the `::` syntax:

```bash
pytest <path-to-test-file>::<test-function-name>
```

For example:
- To run the `test_create_aws_instance` function in `tests/test_aws_api.py`:
  ```bash
  pytest tests/test_aws_api.py::test_create_aws_instance
  ```

#### Running Tests with Verbose Output

To get more detailed output during test execution, use the `-v` flag:

```bash
pytest -v
```

#### Running Tests with Coverage

To check test coverage, install the `pytest-cov` plugin and run:

```bash
pytest --cov=<module-name>
```

For example:
```bash
pytest --cov=azure
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License.