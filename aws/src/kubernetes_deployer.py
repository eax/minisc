import boto3
import sys


class KubernetesDeployer:
    def __init__(self, region='us-east-1'):
        self.ec2 = boto3.client('ec2', region_name=region)
        self.region = region

    def create_vpc_and_subnet(self):
        try:
            # Create VPC
            vpc_response = self.ec2.create_vpc(
                CidrBlock='10.0.0.0/16',
                TagSpecifications=[
                    {
                        'ResourceType': 'vpc',
                        'Tags': [{'Key': 'Name', 'Value': 'kubernetes-vpc'}]
                    }
                ]
            )
            vpc_id = vpc_response['Vpc']['VpcId']

            # Wait for VPC to be available
            waiter = self.ec2.get_waiter('vpc_available')
            waiter.wait(VpcIds=[vpc_id])

            # Enable DNS hostnames
            self.ec2.modify_vpc_attribute(
                VpcId=vpc_id,
                EnableDnsHostnames={'Value': True}
            )

            # Create Internet Gateway
            igw_response = self.ec2.create_internet_gateway()
            igw_id = igw_response['InternetGateway']['InternetGatewayId']

            # Attach Internet Gateway to VPC
            self.ec2.attach_internet_gateway(
                InternetGatewayId=igw_id,
                VpcId=vpc_id
            )

            # Create Subnet
            subnet_response = self.ec2.create_subnet(
                VpcId=vpc_id,
                CidrBlock='10.0.1.0/24',
                TagSpecifications=[
                    {
                        'ResourceType': 'subnet',
                        'Tags': [{'Key': 'Name', 'Value': 'kubernetes-subnet'}]
                    }
                ]
            )
            subnet_id = subnet_response['SubnetId']

            # Create Route Table
            route_table_response = self.ec2.create_route_table(VpcId=vpc_id)
            route_table_id = route_table_response['RouteTable']['RouteTableId']

            # Create Route to Internet Gateway
            self.ec2.create_route(
                RouteTableId=route_table_id,
                DestinationCidrBlock='0.0.0.0/0',
                GatewayId=igw_id
            )

            # Associate Route Table with Subnet
            self.ec2.associate_route_table(
                RouteTableId=route_table_id,
                SubnetId=subnet_id
            )

            return vpc_id, subnet_id
        except Exception as e:
            print(f"Error creating VPC and Subnet: {str(e)}")
            sys.exit(1)

    def create_security_group(self, vpc_id):
        try:
            # Create Security Group
            response = self.ec2.create_security_group(
                GroupName='kubernetes-sg',
                Description='Security group for Kubernetes cluster',
                VpcId=vpc_id
            )
            security_group_id = response['GroupId']

            # Add Inbound Rules
            self.ec2.authorize_security_group_ingress(
                GroupId=security_group_id,
                IpPermissions=[
                    {
                        'IpProtocol': '-1',  # All protocols
                        'FromPort': -1,
                        'ToPort': -1,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                    }
                ]
            )
            return security_group_id
        except Exception as e:
            print(f"Error creating Security Group: {str(e)}")
            sys.exit(1)