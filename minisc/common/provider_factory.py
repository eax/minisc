from enum import Enum
from typing import Union, Dict, Any

# Provider implementations
from minisc.azure.head_node import HeadNodeDeployer as AzureHeadNodeDeployer
from minisc.azure.worker_nodes import WorkerNodesDeployer as AzureWorkerNodesDeployer
from minisc.aws.master_node_deployer import MasterNodeDeployer as AwsMasterNodeDeployer
from minisc.aws.worker_nodes_deployer import WorkerNodesDeployer as AwsWorkerNodesDeployer
from minisc.aws.kubernetes_deployer import KubernetesDeployer as AwsKubernetesDeployer

class CloudProvider(Enum):
    AZURE = "azure"
    AWS = "aws"

class CloudProviderFactory:
    @staticmethod
    def get_provider(provider_type: str, config: Dict[str, Any]):
        if provider_type.lower() == CloudProvider.AZURE.value:
            return {
                "head_node_deployer": AzureHeadNodeDeployer(
                    config['tenant_id'],
                    config['client_id'],
                    config['client_secret'],
                    config['subscription_id']
                ),
                "worker_nodes_deployer": AzureWorkerNodesDeployer(
                    config['tenant_id'],
                    config['client_id'],
                    config['client_secret'],
                    config['subscription_id']
                )
            }
        elif provider_type.lower() == CloudProvider.AWS.value:
            region = config.get('region', 'us-east-1')
            return {
                "kubernetes_deployer": AwsKubernetesDeployer(region),
                "head_node_deployer": AwsMasterNodeDeployer(region),
                "worker_nodes_deployer": AwsWorkerNodesDeployer(region)
            }
        else:
            raise ValueError(f"Unsupported cloud provider: {provider_type}")