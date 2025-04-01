# Azure Kubernetes Deployment Project

This project demonstrates how to deploy a Kubernetes cluster on Azure using the Azure Python SDK. It includes functionality to deploy a Kubernetes head node and worker nodes using Virtual Machines and Virtual Machine Scale Sets (VMSS).

## Project Structure

```
azure
├── src
│   ├── head_node.py          # Logic for deploying the Kubernetes head node
│   ├── worker_nodes.py       # Logic for deploying Kubernetes worker nodes
│   ├── kubernetes_deployer.py # Base class for Kubernetes deployment
│   ├── templates
│   │   ├── cloud_init_head_node.yaml  # Cloud-init template for head node
│   │   └── cloud_init_worker_node.yaml # Cloud-init template for worker nodes
│   └── utils
│       └── azure_helpers.py  # Azure utility functions
├── azure_config.py           # Configuration settings for Azure resources
├── requirements.txt          # Project dependencies
├── .env                      # Environment variables
└── README.md                 # Project documentation
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