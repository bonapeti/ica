from perf_decorator import timeit
from azure.mgmt.resource import ResourceManagementClient
import logging

MISSING_SUBSCRIPTION_ID = "Missing subscription ID"
GET_RESOURCES_EXPAND="createdTime,changedTime,provisioningState"

@timeit
def get_resources(credentials, subscription_id):
    
    assert subscription_id, MISSING_SUBSCRIPTION_ID
    
    print(f"Getting resources from Azure subscription '{subscription_id}'")
    result={}
    with ResourceManagementClient(credentials, subscription_id) as resource_client:
        for resource_group in list(resource_client.resource_groups.list()):
            result[resource_group.name] = []
            for resource in list(resource_client.resources.list_by_resource_group(resource_group.name, expand=GET_RESOURCES_EXPAND)):
                result[resource_group.name].append(resource)
    return result
