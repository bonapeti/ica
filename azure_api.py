from perf_decorator import timeit
from azure.mgmt.resource import ResourceManagementClient
import logging

MISSING_SUBSCRIPTION_ID = "Missing subscription ID"
GET_RESOURCES_EXPAND="createdTime,changedTime,provisioningState"

@timeit
def get_resources(credentials, subscription_id):
    
    assert subscription_id, MISSING_SUBSCRIPTION_ID
    
    logging.debug(f"Getting resource groups with resources from Azure subscription '{subscription_id}'")
    result={}
    with ResourceManagementClient(credentials, subscription_id) as resource_client:
        for resource_group in list(resource_client.resource_groups.list()):
            result[resource_group.name] = []
            for resource in list(resource_client.resources.list_by_resource_group(resource_group.name, expand=GET_RESOURCES_EXPAND)):
                result[resource_group.name].append(resource)
    logging.debug(f"Result: {result}")
    return result



@timeit
def get_resources1(credentials, subscription_id):
    
    assert subscription_id, MISSING_SUBSCRIPTION_ID
    
    logging.debug(f"Getting list of resources from Azure subscription '{subscription_id}'")
    with ResourceManagementClient(credentials, subscription_id) as resource_client:
        return list(resource_client.resources.list(expand=GET_RESOURCES_EXPAND))

@timeit
def get_resource_groups(credentials, subscription_id):
    assert subscription_id, MISSING_SUBSCRIPTION_ID
    
    logging.debug(f"Getting list of resource groups from Azure subscription '{subscription_id}'")
    with ResourceManagementClient(credentials, subscription_id) as resource_client:
        return list(resource_client.resource_groups.list())

@timeit
def get_resources_in_group(credentials, subscription_id, resource_group_name):
    assert subscription_id, MISSING_SUBSCRIPTION_ID
    
    logging.debug(f"Getting list of resources in group '{resource_group_name}' from Azure subscription '{subscription_id}'")
    with ResourceManagementClient(credentials, subscription_id) as resource_client:
        return list(resource_client.resources.list_by_resource_group(resource_group_name,expand=GET_RESOURCES_EXPAND))