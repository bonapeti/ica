import click
from config import save_yaml, load_yaml, new_azure_config
from azure.identity import AzureCliCredential
from azure.identity._exceptions import CredentialUnavailableError
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
        config = load_yaml(stream)

        with AzureCliCredential() as credential:
            for subscription in config.azure.subscriptions:
                azure_api.compare_subscription_with_remote(credential, subscription, click)
        
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
        config = load_yaml(stream)

        with AzureCliCredential() as credential:
            for subscription in config.azure.subscriptions:
                azure_api.update_subscription_from_remote(credential, subscription)
    
        save_yaml(config.yaml_config, open(file,"w"))

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
        credential = AzureCliCredential()
        subscription_client = SubscriptionClient(credential)
        az_subscription = subscription_client.subscriptions.get(subscription_id)

        config = new_azure_config(az_subscription.tenant_id, subscription_id, az_subscription.display_name)

        for subscription in config.azure.subscriptions:
            azure_api.update_subscription_from_remote(credential, subscription)

        save_yaml(config.yaml_config, sys.stdout)

    except KeyError as ke:
        click.echo(str(ke))
    except CredentialUnavailableError as login_error:
        click.echo(str(login_error))   



if __name__ == '__main__':
    main()