import sys
import logging
import click
import core
import config

@click.group()
@click.version_option(version="0.1.0")
@click.option('--debug/--no-debug', default=False)
def main(debug = False):
    """Manages cloud infrastructure as code"""

    if debug:
        logging.basicConfig(level=logging.DEBUG)

@main.command()
@click.option("-c","--cloud", required=True, type=click.Choice(['azure']), help="Supported cloud providers: 'azure'")
@click.option("-s","--subscription_id", required=True, help="Subscription ID")
def show(cloud, subscription_id):
    """Prints cloud infrastructure to stdout as YAML"""

    logging.debug(f"Calling 'show' command, parameters:\"-c {cloud} -s {subscription_id}\"")

    config.print_cloud_resources(core.get_cloud_resources( [ { "type" : cloud, "subscription_ids" : [subscription_id]} ]), sys.stdout)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        click.echo(e)
