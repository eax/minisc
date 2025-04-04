import os
from .kubernetes_deployer import KubernetesDeployer


class WorkerNodesDeployer(KubernetesDeployer):
    def __init__(self, region='us-east-1'):
        super().__init__(region)
        self.worker_instances = []

    def deploy_worker_nodes(self, security_group_id, subnet_id, key_name, num_workers=2, instance_type='t2.medium'):
        try:
            # Load user data script
            script_path = os.path.join(os.path.dirname(__file__), '../scripts/worker_init.sh')
            with open(script_path, 'r') as f:
                user_data = f.read()

            # Get latest Amazon Linux 2 AMI
            response = self.ec2.describe_images(
                Filters=[
                    {'Name': 'name', 'Values': ['amzn2-ami-hvm-*-x86_64-gp2']},
                    {'Name': 'state', 'Values': ['available']}
                ],
                Owners=['amazon']
            )
            ami_id = sorted(response['Images'], key=lambda x: x['CreationDate'], reverse=True)[0]['ImageId']

            # Launch Worker Nodes
            worker_response = self.ec2.run_instances(
                ImageId=ami_id,
                InstanceType=instance_type,
                KeyName=key_name,
                MinCount=num_workers,
                MaxCount=num_workers,
                SecurityGroupIds=[security_group_id],
                SubnetId=subnet_id,
                UserData=user_data,
                TagSpecifications=[
                    {
                        'ResourceType': 'instance',
                        'Tags': [{'Key': 'Name', 'Value': 'k8s-worker'}]
                    }
                ]
            )
            self.worker_instances = worker_response['Instances']
            print(f"{num_workers} worker nodes launched.")
        except Exception as e:
            print(f"Error deploying Worker Nodes: {str(e)}")
            sys.exit(1)