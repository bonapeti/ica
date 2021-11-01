from perf_decorator import timeit
from azure.mgmt.resource import ResourceManagementClient
import logging

@timeit
def get_resources(credentials, subscription_id):
    assert subscription_id, "Missing subscription ID"
    
    logging.debug(f"Getting list of resources from Azure subscription '{subscription_id}'")
    with ResourceManagementClient(credentials, subscription_id) as resource_client:
        return list(resource_client.resources.list(expand="createdTime,changedTime,provisioningState"))

@timeit
def get_resource_groups(credentials, subscription_id):
    assert subscription_id, "Missing subscription ID"
    
    logging.debug(f"Getting list of resource groups from Azure subscription '{subscription_id}'")
    with ResourceManagementClient(credentials, subscription_id) as resource_client:
        return list(resource_client.resource_groups.list())