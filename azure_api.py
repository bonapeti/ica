from azure.identity import AzureCliCredential
from azure.identity._exceptions import CredentialUnavailableError
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.subscriptions import SubscriptionClient

def update_subscription_from_remote(credentials, subscription):
    with ResourceManagementClient(credentials, subscription.id) as resource_client:
        for resource in list(resource_client.resources.list(expand="createdTime,changedTime,provisioningState")):
            subscription.add_resource({"name": resource.name, "type": resource.type })

def compare_subscription_with_remote(credentials, subscription, output):
    with ResourceManagementClient(credentials, subscription.id) as resource_client:
        output.echo(f"Azure subscription '{subscription.name}'")
        if len(list(resource_client.resources.list(expand="createdTime,changedTime,provisioningState"))) == subscription.local_resource_count():
            output.echo("\tNo changes")
        else:
            output.echo("\tThere are differences")


        