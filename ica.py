import click
import yaml
from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient
import pprint

default_filename = "infrastructure.yaml"



@click.group()
@click.version_option(version="0.0.1")
def main():
    """Manages cloud infrastructure with code"""
    pass

@main.command()
@click.option("-f","--file", default=default_filename, show_default=True)
def pull(file):
    f"""Pulls latest changes and updates {file}"""
    column_width = 40
    try:
        stream = open(file,"r")
        configs = yaml.safe_load(stream)
        if configs:
            for config in configs:
                pprint.pprint(config)
                with ResourceManagementClient(AzureCliCredential(), config["subscription"]["id"]) as resource_client:
                    group_list = resource_client.resource_groups.list()
                    print("Resource Group".ljust(column_width) + "Location")
                    print("-" * (column_width * 2))
                    for group in list(group_list):
                        print(f"{group.name:<{column_width}}{group.location}") 
    except FileNotFoundError:
        click.echo(f"Cannot find {file}")
    

if __name__ == '__main__':
    main()