import os
from .kubernetes_deployer import KubernetesDeployer


class MasterNodeDeployer(KubernetesDeployer):
    def __init__(self, region='us-east-1'):
        super().__init__(region)
        self.master_instance = None

    def deploy_master_node(self, security_group_id, subnet_id, key_name, instance_type='t2.medium'):
        try:
            # Load user data script
            script_path = os.path.join(os.path.dirname(__file__), '../scripts/master_init.sh')
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

            # Launch Master Node
            master_response = self.ec2.run_instances(
                ImageId=ami_id,
                InstanceType=instance_type,
                KeyName=key_name,
                MinCount=1,
                MaxCount=1,
                SecurityGroupIds=[security_group_id],
                SubnetId=subnet_id,
                UserData=user_data,
                TagSpecifications=[
                    {
                        'ResourceType': 'instance',
                        'Tags': [{'Key': 'Name', 'Value': 'k8s-master'}]
                    }
                ]
            )
            self.master_instance = master_response['Instances'][0]
            print(f"Master node launched: {self.master_instance['InstanceId']}")
        except Exception as e:
            print(f"Error deploying Master Node: {str(e)}")
            sys.exit(1)