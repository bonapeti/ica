import logging
import sys
import textwrap

import click
from tabulate import tabulate

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
def diff(file):
    """Shows differences between local and remote resources"""

    logging.debug(f"Calling 'diff' command, parameters:\"-f {file}\"")
    with config.open_file_for_read(file) as stream:
        differences = core.calculate_differences(config.load2(stream))
        if len(differences) == 0:
            click.echo("No changes")
        else:
            click.echo("There are differences")
            click.echo("")
            print_differences_with_tabular_format(differences, file)

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

def print_differences_with_tabular_format(differences, file_name):
    formatted = []
    for difference in differences:
        formatted.append([ get_resource_name(difference[0]), format_common(difference[1]), get_resource_name(difference[2])])
    print(tabulate(formatted, headers=[bold(file_name), bold("Difference in properties"), bold("Cloud")], tablefmt="simple", colalign=("left","center","right") ))

def bold(text):
    return "\033[1m" + text + "\033[0m"

FIXED_WIDTH = 100
def format_common(diffs):
    if not diffs:
        return ""

    assert isinstance(diffs, dict), "Expecting dict"
    common_as_string = []
    for resource_name, diff in diffs.items():
        if diff[0] and not diff[1]:
            common_as_string.append(textwrap.shorten(f"{bold(resource_name)}: {diff[0]} <=> ???", width=FIXED_WIDTH))
        elif not diff[0] and diff[1]:
            common_as_string.append(textwrap.shorten(f"{bold(resource_name)}: ??? <=> {diff[1]}", width=FIXED_WIDTH))
        elif diff[0] and diff[1]:
            common_as_string.append(textwrap.shorten(f"{bold(resource_name)}: {diff[0]} <=> {diff[1]}", width=FIXED_WIDTH))
    return "\n".join(common_as_string)

def get_resource_name(resource):
    if not resource:
        return "(Missing)"

    if "name" in resource:
        return resource["name"]
    else:
        return ""

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        click.echo(e)
