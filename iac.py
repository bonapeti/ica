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
        with open(file,"r") as stream:
            config = load_yaml(stream)

            with AzureCliCredential() as credential:
                azure_api.compare_tenant_with_remote(credential, config.azure, click) 
            
    except FileNotFoundError:
        click.echo(f"Cannot find {file}")
    except Exception as e:
        click.echo(str(e))
    
@main.command()
@click.option("-f","--file", default=default_filename, show_default=True, help=CONFIG_FILE_HELP)
def pull(file):
    """Pulls latest cloud info and updates local config file"""

    try:
        with open(file,"r") as stream:
            config = load_yaml(stream)

            with AzureCliCredential() as credential:
                azure_api.update_tenant_from_remote(credential, config.azure) 
        
            save_yaml(config.yaml_config, open(file,"w"))

    except FileNotFoundError:
        click.echo(f"Cannot find {file}")
    except Exception as e:
        click.echo(str(e))

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

        azure_api.update_tenant_from_remote(credential, config.azure)    

        save_yaml(config.yaml_config, sys.stdout)

    except Exception as e:
        click.echo(str(e))



if __name__ == '__main__':
    main()