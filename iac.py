from azure.core import credentials
from azure.mgmt.resource import subscriptions
import click
from config import Config
from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.subscriptions import SubscriptionClient
import sys
import difflib



default_filename = "infrastructure.yaml"


@click.group()
@click.version_option(version="0.0.2")
def main():
    """Manages cloud infrastructure with code"""
    pass

@main.command()
@click.option("-f","--file", default=default_filename, show_default=True)
def status(file):
    f"""Pulls latest changes and updates {file}"""

    try:
        stream = open(file,"r")
        config = Config.load(stream)

        if config.azure.subscriptions is None:
            raise click.ClickException(f"No subscription configured for Azure tenant {config.azure.id}!")

        credentials = AzureCliCredential()
        subscription_client = SubscriptionClient(credentials)
        tenants = list(subscription_client.tenants.list())

        if config.azure.id not in list(map(lambda tenant: tenant.tenant_id, tenants)):
            raise click.ClickException(f"{config.azure.id} not in your tenant list {tenants}!")

        for subscription in config.azure.subscriptions:

            with ResourceManagementClient(credentials, subscription.id) as resource_client:
                resource_list = list(resource_client.resources.list(expand="createdTime,changedTime,provisioningState"))
                print(f"Subscription '{subscription}': local resources: {subscription.local_resource_count()}, remote resources: {len(resource_list)}")
    
    except FileNotFoundError:
        click.echo(f"Cannot find {file}")
    except KeyError as ke:
        click.echo(str(ke))
    
@main.command()
@click.option("-f","--file", default=default_filename, show_default=True)
def pull(file):
    f"""Pulls latest remote resource list and updates local config file"""

    try:
        stream = open(file,"r")
        config = Config.load(stream)

        if config.azure.subscriptions is None:
            raise click.ClickException(f"No subscription configured for Azure tenant {config.azure.id}!")

        credentials = AzureCliCredential()
        subscription_client = SubscriptionClient(credentials)
        tenants = list(subscription_client.tenants.list())

        if config.azure.id not in list(map(lambda tenant: tenant.tenant_id, tenants)):
            raise click.ClickException(f"{config.azure.id} not in your tenant list {tenants}!")

        for subscription in config.azure.subscriptions:

            with ResourceManagementClient(credentials, subscription.id) as resource_client:
                resource_list = list(resource_client.resources.list(expand="createdTime,changedTime,provisioningState"))
                for resource in resource_list:
                    subscription.add_resource({"name": resource.name, "type": resource.type })
    
        config.save(open(file,"w"))

    except FileNotFoundError:
        click.echo(f"Cannot find {file}")
    except KeyError as ke:
        click.echo(str(ke))
    

@main.command()
@click.option("-t","--type", default="azure", show_default=True)
@click.option("-s","--subscription_id", required=True)
def describe(type, subscription_id):
    f"""Pulls latest remote resource list prints as YAML configutation to stdout"""

    try:
        credentials = AzureCliCredential()
        subscription_client = SubscriptionClient(credentials)
        az_subscription = subscription_client.subscriptions.get(subscription_id)
        tenant_list = list(subscription_client.tenants.list())
        
        tenant_name = [tenant.display_name for tenant in tenant_list if tenant.id == f"/tenants/{az_subscription.tenant_id}"][0] 

        output_yaml=f"""\
- cloud: azure
  name: {tenant_name}
  tenantId: {az_subscription.tenant_id}
  subscriptions:
  - id: {subscription_id}
    name: {az_subscription.display_name}
"""
        config = Config.load(output_yaml)
        subscription = config.azure.subscriptions[0]

        with ResourceManagementClient(credentials, subscription_id) as resource_client:
            resource_list = list(resource_client.resources.list(expand="createdTime,changedTime,provisioningState"))
            for resource in resource_list:
                subscription.add_resource({"name": resource.name, "type": resource.type })

        config.save(sys.stdout)

    except KeyError as ke:
        click.echo(str(ke))
    


if __name__ == '__main__':
    main()