from azure.core import credentials
from azure.mgmt.resource import subscriptions
import click
from config import Config
from azure.identity import AzureCliCredential
from azure.identity._exceptions import CredentialUnavailableError
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.subscriptions import SubscriptionClient
import sys
import azure_api

default_filename = "infrastructure.yaml"
CONFIG_FILE_HELP="YAML file describing infrastructure"

@click.group()
@click.version_option(version="0.0.2")
def main():
    """Manages cloud infrastructure as code"""
    pass

@main.command()
@click.option("-f","--file", default=default_filename, show_default=True, help=CONFIG_FILE_HELP)
def status(file):
    """Shows differences between local and cloud infrastructure"""

    try:
        stream = open(file,"r")
        config = Config.load(stream)

        subscription_resources = azure_api.get_resource_list(config.azure.id, config.azure.subscriptions )

        for subscription, resource_list in subscription_resources.items():
            click.echo(f"Azure subscription '{subscription.name}'")
            if len(resource_list) == subscription.local_resource_count():
                click.echo("\tNo changes")
            else:
                click.echo("\tThere are differences")
    
    except FileNotFoundError:
        click.echo(f"Cannot find {file}")
    except KeyError as ke:
        click.echo(str(ke))
    except CredentialUnavailableError as login_error:
        click.echo(str(login_error))
    
@main.command()
@click.option("-f","--file", default=default_filename, show_default=True, help=CONFIG_FILE_HELP)
def pull(file):
    """Pulls latest cloud info and updates local config file"""

    try:
        stream = open(file,"r")
        config = Config.load(stream)

        subscription_resources = azure_api.get_resource_list(config.azure.id, config.azure.subscriptions)

        for subscription, resource_list in subscription_resources.items():
            for resource in resource_list:
                subscription.add_resource({"name": resource.name, "type": resource.type })
    
        config.save(open(file,"w"))

    except FileNotFoundError:
        click.echo(f"Cannot find {file}")
    except KeyError as ke:
        click.echo(str(ke))
    except CredentialUnavailableError as login_error:
        click.echo(str(login_error))    

@main.command()
@click.option("-t","--type", required=True, type=click.Choice(['azure']), help="One of supported cloud provider: 'azure'")
@click.option("-s","--subscription_id", required=True, help="Subscription ID")
def describe(type, subscription_id):
    """Prints cloud infrastructure to stdout as YAML"""

    assert type == 'azure', "The supported cloud providers are: ['azure']"
    try:
        credentials = AzureCliCredential()
        subscription_client = SubscriptionClient(credentials)
        az_subscription = subscription_client.subscriptions.get(subscription_id)
        
        output_yaml=f"""\
- cloud: azure
  tenantId: {az_subscription.tenant_id}
  subscriptions:
  - id: {subscription_id}
    name: {az_subscription.display_name}
"""
        config = Config.load(output_yaml)

        subscription_resources = azure_api.get_resource_list(config.azure.id, config.azure.subscriptions)

        for subscription, resource_list in subscription_resources.items():
            for resource in resource_list:
                subscription.add_resource({"name": resource.name, "type": resource.type })

        config.save(sys.stdout)

    except KeyError as ke:
        click.echo(str(ke))
    except CredentialUnavailableError as login_error:
        click.echo(str(login_error))   


if __name__ == '__main__':
    main()