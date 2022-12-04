from tabulate import tabulate
import core
import textwrap

def print_as_tree(output, differences, local_resource_name, remote_resource_name):

    output.write("\n".join([ new_resource_action.get_resource_name() for new_resource_action in differences if isinstance(new_resource_action,core.LocalOnlyResourceDifference)]))
    output.write("\n".join([ new_resource_action.get_resource_name() for new_resource_action in differences if isinstance(new_resource_action,core.ResourceAttributeDifferences)]))
    output.write("\n".join([ new_resource_action.get_resource_name() for new_resource_action in differences if isinstance(new_resource_action,core.RemoteOnlyResourceDifference)]))



def print_as_table(output, differences, local_resource_name, remote_resource_name):
    formatted = []
    for difference in differences:
        formatted.append([display_change_in_local_config(difference), display_attribute_differences(difference), display_change_in_remote_config(difference)])
    output.write(tabulate(formatted, headers=[bold(local_resource_name), bold("Property differences"), bold(remote_resource_name)], tablefmt="simple", colalign=("left","center","right") ))

FIXED_WIDTH = 100
def bold(text):
    return "\033[1m" + text + "\033[0m"


def display_change_in_local_config(difference):
    if not difference:
        return "M/A"

    if isinstance(difference, core.LocalOnlyResourceDifference) or isinstance(difference, core.ResourceAttributeDifferences):
        return difference.get_resource_name()

    return "(Missing)"

def get_value(value):
    if value:
        return value
    return "???"

def display_attribute_differences(difference):
    if isinstance(difference, core.ResourceAttributeDifferences):
        common_as_string = []
        for resource_name, diff in difference.attribute_differences.items():
            local_value = get_value(diff[0])
            remote_value = get_value(diff[1])
            common_as_string.append(textwrap.shorten(f"{bold(resource_name)}: {local_value} <=> {remote_value}", width=FIXED_WIDTH))
        return "\n".join(common_as_string)

    return ""



def display_change_in_remote_config(difference):
    if not difference:
        return "M/A"

    if isinstance(difference, core.RemoteOnlyResourceDifference) or isinstance(difference, core.ResourceAttributeDifferences):
        return difference.get_resource_name()

    return "(Missing)"
