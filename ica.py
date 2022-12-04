import logging
import sys
import output_format

import click

import config
import core

DEFAULT_FILENAME = "infrastructure.yaml"
CONFIG_FILE_HELP="YAML file describing infrastructure"

@click.group()
@click.version_option(version="0.2.0")
@click.option('--debug/--no-debug', default=False)
def main(debug = False):
    """Manages cloud resources with YAML code"""

    if debug:
        logging.basicConfig(level=logging.DEBUG)

@main.command()
@click.option("-c", "--cloud", required=True, type=click.Choice(['azure']), help="Supported cloud providers: 'azure'")
@click.option("-s", "--subscription_id", required=True, help="Subscription ID")
def show(cloud, subscription_id):
    """Prints cloud resource descriptions to stdout as YAML"""

    logging.debug(f"Calling 'show' command, parameters:\"-c {cloud} -s {subscription_id}\"")
    core.print_cloud_resources(cloud, subscription_id, sys.stdout)


@main.command()
@click.option("-f", "--file", default=DEFAULT_FILENAME, show_default=True, help=CONFIG_FILE_HELP)
@click.option("-o", "--output", type=click.Choice(['table', 'tree'], case_sensitive=True), default="table", show_default=True, help="Output format")
def diff(file, output):
    """Shows differences between local and remote resources"""

    logging.debug(f"Calling 'diff' command, parameters:\"-f {file}\"")
    with config.open_file_for_read(file) as stream:
        differences = core.calculate_differences(config.load2(stream))
        if len(differences) == 0:
            click.echo("No changes")
        else:
            click.echo("There are differences")
            click.echo("")
            if output == "table":
                output_format.print_as_table(sys.stdout, differences, file, "Cloud")
            else:
                output_format.print_as_tree(sys.stdout, differences, file, "Cloud")

@main.command()
@click.option("-f", "--file", default=DEFAULT_FILENAME, show_default=True, help=CONFIG_FILE_HELP)
def pull(file):
    """Updates local configuration with remote changes"""

    logging.debug(f"Calling 'pull' command, parameters:\"-f {file}\"")
    with config.open_file_for_read(file) as stream:
        local_config = config.load2(stream)
        modified_local_config = core.apply_remote_changes(local_config)
        if not modified_local_config:
            click.echo("No changes")
        else:
            with config.open_file_for_write(file) as stream:
                config.save2(stream, modified_local_config)
                click.echo(f"Updated {file}")

@main.command()
@click.option("-f", "--file", default=DEFAULT_FILENAME, show_default=True, help=CONFIG_FILE_HELP)
def push(file):
    """Updates resources in cloud with changes in local configuration"""

    logging.debug(f"Calling 'push' command, parameters:\"-f {file}\"")
    with config.open_file_for_read(file) as stream:
        local_config = config.load2(stream)
        change_results = core.apply_local_changes(local_config)

        for change, result in change_results.items():
            print(f"{change}: {result}")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        click.echo(e)
