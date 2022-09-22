from re import S
import sys
import logging
import click
import core
import config

DEFAULT_FILENAME = "infrastructure.yaml"
CONFIG_FILE_HELP="YAML file describing infrastructure"

@click.group()
@click.version_option(version="0.1.0")
@click.option('--debug/--no-debug', default=False)
def main(debug = False):
    """Manages cloud resources with YAML code"""

    if debug:
        logging.basicConfig(level=logging.DEBUG)

@main.command()
@click.option("-c","--cloud", required=True, type=click.Choice(['azure']), help="Supported cloud providers: 'azure'")
@click.option("-s","--subscription_id", required=True, help="Subscription ID")
def show(cloud, subscription_id):
    """Prints cloud resource descriptions to stdout as YAML"""

    logging.debug(f"Calling 'show' command, parameters:\"-c {cloud} -s {subscription_id}\"")
    core.print_cloud_resources(cloud, subscription_id, sys.stdout)


@main.command()
@click.option("-f","--file", default=DEFAULT_FILENAME, show_default=True, help=CONFIG_FILE_HELP)
def diff(file):
    """Shows differences between local and remote resources"""

    logging.debug(f"Calling 'diff' command, parameters:\"-f {file}\"")
    with config.open_file_for_read(file) as stream:
        differences = core.calculate_differences(config.load2(stream))
        if len(differences) ==0:
            click.echo(f"Azure subscription '5ed44b1f-1379-4af2-b7c5-097bbd2e2ee2'\nNo changes")
        else:
            click.echo(f"Azure subscription '5ed44b1f-1379-4af2-b7c5-097bbd2e2ee2'\nThere are differences:")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        click.echo(e)
