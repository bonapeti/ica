"""All Azure API related functions"""
import azure.identity
import azure.mgmt.resource
import azure.mgmt.resource.resources.models
import azure.core.exceptions
import perf_decorator
import azure_yaml

MISSING_SUBSCRIPTION_ID = "Missing subscription ID"
GET_RESOURCES_EXPAND="createdTime,changedTime,provisioningState"
AVAILABLE_REGIONS = {
    'centralus',
    'eastasia',
    'southeastasia',
    'eastus',
    'eastus2',
    'westus',
    'westus2',
    'northcentralus',
    'southcentralus',
    'westcentralus',
    'northeurope',
    'westeurope',
    'japaneast',
    'japanwest',
    'brazilsouth',
    'australiasoutheast',
    'australiaeast',
    'westindia',
    'southindia',
    'centralindia',
    'canadacentral',
    'canadaeast',
    'uksouth',
    'ukwest',
    'koreacentral',
    'koreasouth',
    'francecentral',
    'southafricanorth',
    'uaenorth',
    'australiacentral',
    'switzerlandnorth',
    'germanywestcentral',
    'norwayeast',
    'jioindiawest',
    'westus3',
    'qatarcentral',
    'swedencentral',
    'australiacentral2'}

def login():
    """Logs in and returns AzureCredentials"""
    return azure.identity.AzureCliCredential()

def validate_location(location_name: str):
    if location_name not in AVAILABLE_REGIONS:
        raise ValueError(f"'{location_name}' is not an Azure supported region")

@perf_decorator.timeit
def get_resources(credentials, subscription_id) -> dict:
    """Returns all resources groups and resources as dictionary"""
    assert subscription_id, MISSING_SUBSCRIPTION_ID

    result={}
    with azure.mgmt.resource.ResourceManagementClient(credentials, subscription_id) as resource_client:
        for resource_group in list(resource_client.resource_groups.list()):
            result[resource_group.name] = { azure_yaml.YAML_AZURE_RESOURCE_NAME: resource_group.name, azure_yaml.YAML_AZURE_RESOURCE_LOCATION: resource_group.location }
            resources = {}
            result[resource_group.name][azure_yaml.YAML_RESOURCE_GROUPS] = resources
            for resource in __get_resources_in_resource_group(resource_client, resource_group.name):
                resources[resource.name] = { azure_yaml.YAML_AZURE_RESOURCE_NAME: resource.name }
    return result

def __get_resources_in_resource_group(resource_client: azure.mgmt.resource.ResourceManagementClient,
                                        name: str) -> list:
    """Calls resource_client.resources.list_by_resource_group"""
    assert resource_client, "Missing resource client"
    assert name, "Missing resource group name"
    return list(resource_client.resources.list_by_resource_group(name, expand=GET_RESOURCES_EXPAND))

@perf_decorator.timeit
def update_resource_group(credentials, subscription_id, resource_group_name: str, resource_group: dict) -> None:
    assert credentials, "Missing credentials"
    assert subscription_id, "Missing subscription ID"
    assert resource_group_name, "Missing resource group name"
    assert resource_group, "Missing resource group"
    assert resource_group[azure_yaml.YAML_AZURE_RESOURCE_LOCATION], "Missing resource group location"
    validate_location(resource_group[azure_yaml.YAML_AZURE_RESOURCE_LOCATION])

    with azure.mgmt.resource.ResourceManagementClient(credentials, subscription_id) as resource_client:
        azure_resource_group = azure.mgmt.resource.resources.models.ResourceGroup(location=resource_group[azure_yaml.YAML_AZURE_RESOURCE_LOCATION],
                                            name=resource_group_name,
                                            properties={

                                            })
        resource_client.resource_groups.create_or_update(resource_group_name, parameters = azure_resource_group)

@perf_decorator.timeit
def delete_resource_group(credentials, subscription_id, resource_group_name, ignore_missing=True) -> None:
    assert credentials, "Missing credentials"
    assert subscription_id, "Missing subscription ID"
    assert resource_group_name, "Missing resource group name"

    with azure.mgmt.resource.ResourceManagementClient(credentials, subscription_id) as resource_client:
        try:
            resource_client.resource_groups.begin_delete(resource_group_name).wait()
        except azure.core.exceptions.ResourceNotFoundError as rnfe:
            if not ignore_missing:
                raise rnfe

@perf_decorator.timeit
def check_existence(credentials, subscription_id, resource_group_name) -> bool:
    assert credentials, "Missing credentials"
    assert subscription_id, "Missing subscription ID"
    assert resource_group_name, "Missing resource group name"

    with azure.mgmt.resource.ResourceManagementClient(credentials, subscription_id) as resource_client:
        return resource_client.resource_groups.check_existence(resource_group_name)
