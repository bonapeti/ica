"""All Azure API related functions"""
from azure.mgmt.resource import ResourceManagementClient
from perf_decorator import timeit

MISSING_SUBSCRIPTION_ID = "Missing subscription ID"
GET_RESOURCES_EXPAND="createdTime,changedTime,provisioningState"

@timeit
def get_resources(credentials, subscription_id) -> dict:
    """Returns all resources groups and resources as dictionary"""
    assert subscription_id, MISSING_SUBSCRIPTION_ID

    result={}
    with ResourceManagementClient(credentials, subscription_id) as resource_client:
        for resource_group in list(resource_client.resource_groups.list()):
            result[resource_group.name] = []
            for resource in __get_resources_in_resource_group(resource_client, resource_group.name):
                result[resource_group.name].append(resource)
    return result

def __get_resources_in_resource_group(resource_client: ResourceManagementClient,
                                        name: str) -> list:
    """Calls resource_client.resources.list_by_resource_group"""
    assert resource_client, "Missing resource client"
    assert name, "Missing resource group name"
    return list(resource_client.resources.list_by_resource_group(name, expand=GET_RESOURCES_EXPAND))
