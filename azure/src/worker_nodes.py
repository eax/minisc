import base64
import os
from string import Template
from azure.mgmt.compute.models import (
    VirtualMachineScaleSet,
    VirtualMachineScaleSetSku,
    VirtualMachineScaleSetVMProfile,
    VirtualMachineScaleSetOSProfile,
    VirtualMachineScaleSetNetworkProfile,
    NetworkInterfaceConfiguration,
    IPConfiguration
)
from .kubernetes_deployer import KubernetesDeployer

class WorkerNodesDeployer(KubernetesDeployer):
    def create_kubernetes_worker_nodes(self, group_name, vmss_name, location, vm_size, instance_count,
                                       vnet_name, subnet_name, admin_username, admin_password,
                                       master_ip, join_token=None):
        # Ensure VNet and subnet exist
        self._ensure_network_exists(group_name, location, vnet_name, subnet_name)

        # Get subnet ID
        subnet = self.network_client.subnets.get(group_name, vnet_name, subnet_name)
        subnet_id = subnet.id

        # Load and render cloud-init template
        template_path = os.path.join(os.path.dirname(__file__), "templates/cloud_init_worker_node.yaml")
        with open(template_path, "r") as file:
            template = Template(file.read())
            cloud_init_script = template.substitute(
                MASTER_IP=master_ip,
                JOIN_TOKEN=join_token or "",
                ADMIN_USERNAME=admin_username
            )

        vmss_params = VirtualMachineScaleSet(
            location=location,
            sku=VirtualMachineScaleSetSku(name=vm_size, tier='Standard', capacity=instance_count),
            upgrade_policy={"mode": "Manual"},
            virtual_machine_profile=VirtualMachineScaleSetVMProfile(
                os_profile=VirtualMachineScaleSetOSProfile(
                    computer_name_prefix=vmss_name,
                    admin_username=admin_username,
                    admin_password=admin_password,
                    custom_data=base64.b64encode(cloud_init_script.encode()).decode()
                ),
                storage_profile={
                    "image_reference": {
                        "publisher": "Canonical",
                        "offer": "UbuntuServer",
                        "sku": "24_04-lts",
                        "version": "latest"
                    },
                    "os_disk": {
                        "create_option": "FromImage",
                        "caching": "ReadWrite",
                        "managed_disk": {
                            "storage_account_type": "Premium_LRS"
                        }
                    }
                },
                network_profile=VirtualMachineScaleSetNetworkProfile(
                    network_interface_configurations=[
                        NetworkInterfaceConfiguration(
                            name='nic',
                            primary=True,
                            ip_configurations=[
                                IPConfiguration(
                                    name='ipconfig',
                                    subnet={"id": subnet_id}
                                )
                            ]
                        )
                    ]
                )
            )
        )

        creation = self.compute_client.virtual_machine_scale_sets.begin_create_or_update(
            group_name, vmss_name, vmss_params
        )
        vmss = creation.result()
        print(f"Kubernetes worker nodes VMSS '{vmss_name}' with {instance_count} instances created.")
        print("Note: For the nodes to join the cluster, you'll need to get the join token from the master node")
        print("      and manually join each worker or update the VMSS instances.")

        return vmss