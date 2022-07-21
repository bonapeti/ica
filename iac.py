import click
from config import load_yaml, new_azure_config, save_yaml
from azure.identity import AzureCliCredential
import sys
import logging

default_filename = "infrastructure.yaml"
CONFIG_FILE_HELP="YAML file describing infrastructure"

@click.group()
@click.version_option(version="0.0.3")
@click.option('--debug/--no-debug', default=False)
def main(debug):
    """Manages cloud infrastructure as code"""

    if debug:
        logging.basicConfig(level=logging.DEBUG)

@main.command()
@click.option("-f","--file", default=default_filename, show_default=True, help=CONFIG_FILE_HELP)
def diff(file):
    """Shows differences between local and cloud infrastructure"""

    logging.debug(f"Calling 'diff' command with config file {file}")
    try:
        with open(file,"r") as stream:
            local_config = load_yaml(stream)

            with AzureCliCredential() as credential:
                local_config.compare_with_remote(credential, click) 
            
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
            local_config = load_yaml(stream)

            with AzureCliCredential() as credential:
                local_config.update_from_remote(credential) 
        
            save_yaml(local_config.as_yaml(),open(file,"w"))

    except FileNotFoundError:
        click.echo(f"Cannot find {file}")
    except Exception as e:
        click.echo(str(e))

@main.command()
@click.option("-t","--type", required=True, type=click.Choice(['azure']), help="One of supported cloud provider: 'azure'")
@click.option("-s","--subscription_id", required=True, help="Subscription ID")
def show(type, subscription_id):
    """Prints cloud infrastructure to stdout as YAML"""

    logging.debug("Calling 'show' command")
    assert type == 'azure', "The supported cloud providers are: ['azure']"
    try:
        local_config = new_azure_config(subscription_id)
        
        with AzureCliCredential() as credential:
            local_config.update_from_remote(credential)    

        save_yaml(local_config.as_yaml(), sys.stdout)

    except Exception as e:
        click.echo(str(e))



if __name__ == '__main__':
    main()