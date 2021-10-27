from azure.identity import AzureCliCredential
from azure.identity._exceptions import CredentialUnavailableError
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.subscriptions import SubscriptionClient

def update_tenant_from_remote(credential, tenant):
    for subscription in tenant.subscriptions:
        update_subscription_from_remote(credential, subscription)

def compare_tenant_with_remote(credential, tenant, output):
    for subscription in tenant.subscriptions:
        compare_subscription_with_remote(credential, subscription, output)

def update_subscription_from_remote(credentials, subscription):
    with ResourceManagementClient(credentials, subscription.id) as resource_client:
        for resource in get_resources(resource_client):
            subscription.add_resource({"name": resource.name, "type": resource.type })

def get_resources(resource_client):
    return list(resource_client.resources.list(expand="createdTime,changedTime,provisioningState"))

def compare_subscription_with_remote(credentials, subscription, output):
    with ResourceManagementClient(credentials, subscription.id) as resource_client:
        output.echo(f"Azure subscription '{subscription.name}'")
        if len(get_resources(resource_client)) == subscription.local_resource_count():
            output.echo("\tNo changes")
        else:
            output.echo("\tThere are differences")


        