"""Command line entry point for IAC"""
import sys
import logging
import click
from cloud.azure.api import login
from config import load_yaml, new_azure_config, save_yaml

DEFAULT_FILENAME = "infrastructure.yaml"
CONFIG_FILE_HELP="YAML file describing infrastructure"

@click.group()
@click.version_option(version="0.0.3")
@click.option('--debug/--no-debug', default=False)
def main(debug = False):
    """Manages cloud infrastructure with YAML"""

    if debug:
        logging.basicConfig(level=logging.DEBUG)

def open_file_for_read(file):
    """Opens file for reading with utf-8 encoding"""
    return open(file,"r", encoding="utf-8")

def open_file_for_write(file):
    """Opens file for writing with utf-8 encoding"""
    return open(file,"w", encoding="utf-8")

@main.command()
@click.option("-f","--file", default=DEFAULT_FILENAME, show_default=True, help=CONFIG_FILE_HELP)
def diff(file):
    """Shows differences between local and cloud infrastructure"""

    logging.debug("Calling 'diff' command with config file %s", file)
    try:
        with open_file_for_read(file) as stream:
            local_config = load_yaml(stream)

            with login() as credential:
                local_config.compare_with_remote(credential, click)

    except FileNotFoundError:
        click.echo(f"Cannot find {file}")

@main.command()
@click.option("-f","--file", default=DEFAULT_FILENAME, show_default=True, help=CONFIG_FILE_HELP)
def pull(file):
    """Pulls latest cloud info and updates local config file"""

    try:
        with open_file_for_read(file) as stream:
            local_config = load_yaml(stream)

            with login() as credential:
                local_config.update_from_remote(credential)

            with open_file_for_write(file) as output:
                save_yaml(local_config.as_yaml(),output)

    except FileNotFoundError:
        click.echo(f"Cannot find {file}")

@main.command()
@click.option("-f","--file", default=DEFAULT_FILENAME, show_default=True, help=CONFIG_FILE_HELP)
def push(file):
    """Pushes latest local changes to cloud"""

    try:
        with open_file_for_read(file) as stream:
            local_config = load_yaml(stream)

            with login() as credential:
                local_config.push(credential)

    except FileNotFoundError:
        click.echo(f"Cannot find {file}")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        click.echo(str(e))
