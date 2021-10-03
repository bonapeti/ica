from azure.core import credentials
import click
from config import Config
from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.subscriptions import SubscriptionClient

import pprint

default_filename = "infrastructure.yaml"


@click.group()
@click.version_option(version="0.0.1")
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
            raise click.ClickException(f"Non subscriptions configured for Azure tenant {config.azure.id}!")

        credentials = AzureCliCredential()
        subscription_client = SubscriptionClient(credentials)
        tenants = list(subscription_client.tenants.list())

        if config.azure.id not in map(lambda tenant: tenant.tenant_id, tenants):
            raise click.ClickException(f"{config.azure.id} not in your tenant list {tenants}!")

        for config in config.azure.subscriptions:
            local_resources = config.get("resources",[])
            print(f"Locally managed resources: {len(local_resources)}")

            with ResourceManagementClient(credentials, config["subscription"]["id"]) as resource_client:
                resource_list = list(resource_client.resources.list())
                print(f"Remotely managed resources: {len(resource_list)}") 
    except FileNotFoundError:
        click.echo(f"Cannot find {file}")
    

if __name__ == '__main__':
    main()