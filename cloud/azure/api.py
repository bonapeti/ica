"""All Azure API related functions"""
import importlib
import logging
from unicodedata import name
from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.resources.models import ResourceGroup
from azure.core.exceptions import ResourceNotFoundError, ClientAuthenticationError
from perf_decorator import timeit
import attributes

YAML_RESOURCES="resources"
YAML_AZURE_RESOURCE_NAME="name"
YAML_AZURE_RESOURCE_LOCATION="location"

SUBSCRIPTION_IDS = "subscription_ids"
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

def azure_exceptions(func):
    """Decorator to translate Azure excaptions"""
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ClientAuthenticationError as cae:
            logging.debug(cae)
            message = "Azure login failed!"
            if cae.message.index("InvalidAuthenticationTokenTenant") != 0:
                message = message + f" You may be using invalid Azure tenant. Login with Azure CLI: 'az logout && az login'"
            raise RuntimeError(message)
    return inner

def login():
    """Logs in and returns AzureCredentials"""
    return AzureCliCredential()

def validate_location(location_name: str):
    if location_name not in AVAILABLE_REGIONS:
        raise ValueError(f"'{location_name}' is not an Azure supported region")

@timeit
@azure_exceptions
def get_all_resources(credentials, subscription_id) -> list:
    """Returns all resources groups as list"""
    assert subscription_id, MISSING_SUBSCRIPTION_ID
    resources = []
    with ResourceManagementClient(credentials, subscription_id) as resource_client:
        for resource_group in resource_client.resource_groups.list():
            resources.append(to_yaml(resource_group))
        for resource in resource_client.resources.list(expand=GET_RESOURCES_EXPAND):
            resources.append(to_yaml(resource))
    return resources

default_resource_attributes = {
                    "name" : {},
                    "type" : {},
                     "location" : {},
                     "tags" : {  },
                     "managed_by" : {  }
                    }

def to_yaml(azure_resource):
    azure_resource_type = azure_resource.type
    try:
        return to_yaml_by_type(azure_resource)
    except ModuleNotFoundError:
        logging.warn(f"Azure resource type '{azure_resource_type}' is not fully supported yet")
        return attributes.object_as_yaml(azure_resource, default_resource_attributes)

def to_yaml_by_type(azure_resource):
    azure_resource_type = azure_resource.type
    module_name = azure_resource_type.replace("/",".")
    azure_resource_type_module = importlib.import_module("." + module_name, "cloud.azure")
    yaml_attributes = getattr(azure_resource_type_module,"yaml_attributes")
    return attributes.object_as_yaml(azure_resource, yaml_attributes)

@timeit
def update_resource_group(credentials, subscription_id, resource_group_name: str, resource_group: dict) -> None:
    assert credentials, "Missing credentials"
    assert subscription_id, "Missing subscription ID"
    assert resource_group_name, "Missing resource group name"
    assert resource_group, "Missing resource group"
    assert resource_group[YAML_AZURE_RESOURCE_LOCATION], "Missing resource group location"
    validate_location(resource_group[YAML_AZURE_RESOURCE_LOCATION])

    logging.debug(f"Updating resource group '{resource_group_name}' in subscription '{subscription_id}' with {resource_group}")

    with ResourceManagementClient(credentials, subscription_id) as resource_client:
        azure_resource_group = ResourceGroup(location=resource_group[YAML_AZURE_RESOURCE_LOCATION],
                                            properties=resource_group)
        resource_client.resource_groups.create_or_update(resource_group_name, parameters = azure_resource_group)

@timeit
def delete_resource_group(credentials, subscription_id, resource_group_name, ignore_missing=True) -> None:
    assert credentials, "Missing credentials"
    assert subscription_id, "Missing subscription ID"
    assert resource_group_name, "Missing resource group name"

    logging.debug(f"Deleting resource group '{resource_group_name}' in subscription '{subscription_id}'")

    with ResourceManagementClient(credentials, subscription_id) as resource_client:
        try:
            resource_client.resource_groups.begin_delete(resource_group_name).wait()
        except ResourceNotFoundError as rnfe:
            if not ignore_missing:
                raise rnfe

@timeit
def check_existence(credentials, subscription_id, resource_group_name) -> bool:
    assert credentials, "Missing credentials"
    assert subscription_id, "Missing subscription ID"
    assert resource_group_name, "Missing resource group name"

    with ResourceManagementClient(credentials, subscription_id) as resource_client:
        return resource_client.resource_groups.check_existence(resource_group_name)
