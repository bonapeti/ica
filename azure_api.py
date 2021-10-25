from azure.identity import AzureCliCredential
from azure.identity._exceptions import CredentialUnavailableError
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.subscriptions import SubscriptionClient


def get_resource_list(tenant_id, subscriptions):
    if subscriptions is None:
        raise ValueError(f"No subscription configured for Azure tenant {tenant_id}!")

    with AzureCliCredential() as credentials:
        subscription_resources = {}
        with SubscriptionClient(credentials) as subscription_client:
            tenants = list(subscription_client.tenants.list())

            if tenant_id not in list(map(lambda tenant: tenant.tenant_id, tenants)):
                raise ValueError(f"{tenant_id} not in your tenant list {tenants}!")

            for subscription in subscriptions:
                with ResourceManagementClient(credentials, subscription.id) as resource_client:
                    subscription_resources[subscription] = list(resource_client.resources.list(expand="createdTime,changedTime,provisioningState"))

        return subscription_resources
        