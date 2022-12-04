from tabulate import tabulate
import core
import textwrap

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

def display_attribute_differences(difference):
    if isinstance(difference, core.ResourceAttributeDifferences):
        common_as_string = []
        for resource_name, diff in difference.attribute_differences.items():
            if diff[0] and not diff[1]:
                common_as_string.append(textwrap.shorten(f"{bold(resource_name)}: {diff[0]} <=> ???", width=FIXED_WIDTH))
            elif not diff[0] and diff[1]:
                common_as_string.append(textwrap.shorten(f"{bold(resource_name)}: ??? <=> {diff[1]}", width=FIXED_WIDTH))
            elif diff[0] and diff[1]:
                common_as_string.append(textwrap.shorten(f"{bold(resource_name)}: {diff[0]} <=> {diff[1]}", width=FIXED_WIDTH))
        return "\n".join(common_as_string)

    return ""

def display_change_in_remote_config(difference):
    if not difference:
        return "M/A"

    if isinstance(difference, core.RemoteOnlyResourceDifference) or isinstance(difference, core.ResourceAttributeDifferences):
        return difference.get_resource_name()

    return "(Missing)"
