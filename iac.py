import click
from config import save_yaml, load_yaml, new_azure_config, compare_tenant_with_remote
from azure.identity import AzureCliCredential
from azure.mgmt.resource.subscriptions import SubscriptionClient
import sys
import logging

default_filename = "infrastructure.yaml"
CONFIG_FILE_HELP="YAML file describing infrastructure"

@click.group()
@click.version_option(version="0.0.2")
@click.option('--debug/--no-debug', default=False)
def main(debug):
    """Manages cloud infrastructure as code"""
    if debug:
        logging.basicConfig(level=logging.DEBUG)

@main.command()
@click.option("-f","--file", default=default_filename, show_default=True, help=CONFIG_FILE_HELP)
def status(file):
    """Shows differences between local and cloud infrastructure"""

    logging.debug(f"Calling 'status' command with config file {file}")
    try:
        with open(file,"r") as stream:
            yaml_config = load_yaml(stream)

            with AzureCliCredential() as credential:
                compare_tenant_with_remote(credential, yaml_config.azure, click) 
            
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
            yaml_config = load_yaml(stream)

            with AzureCliCredential() as credential:
                yaml_config.azure.update_from_remote(credential) 
        
            save_yaml(yaml_config.yaml_config, open(file,"w"))

    except FileNotFoundError:
        click.echo(f"Cannot find {file}")
    except Exception as e:
        click.echo(str(e))

@main.command()
@click.option("-t","--type", required=True, type=click.Choice(['azure']), help="One of supported cloud provider: 'azure'")
@click.option("-s","--subscription_id", required=True, help="Subscription ID")
def describe(type, subscription_id):
    """Prints cloud infrastructure to stdout as YAML"""

    logging.debug("Calling 'desribe' command")
    assert type == 'azure', "The supported cloud providers are: ['azure']"
    try:
        credential = AzureCliCredential()
        subscription_client = SubscriptionClient(credential)
        az_subscription = subscription_client.subscriptions.get(subscription_id)

        yaml_config = new_azure_config(az_subscription.tenant_id, subscription_id, az_subscription.display_name)

        yaml_config.azure.update_from_remote(credential)    

        save_yaml(yaml_config.yaml_config, sys.stdout)

    except Exception as e:
        click.echo(str(e))



if __name__ == '__main__':
    main()