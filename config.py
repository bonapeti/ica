import logging
from ruamel.yaml import YAML
import cloud.azure.api
from tabulate import tabulate
import azure_yaml

SUPPORTED_PROVIDERS=[azure_yaml.AZURE]

def print_cloud_resources(cloud_resources, output) -> None:
    ruamel_yaml = YAML()
    ruamel_yaml.dump(cloud_resources, output)

def open_file_for_read(file):
    """Opens file for reading with utf-8 encoding"""
    logging.debug(f"Opening file '{file}'")
    return open(file,"r", encoding="utf-8")

def open_file_for_write(file):
    """Opens file for writing with utf-8 encoding"""
    return open(file,"w", encoding="utf-8")

def expect_string(dict_var, name, error_message):
    value = dict_var.get(name)
    if value is None:
        raise ValueError(error_message)
    assert isinstance(value, str)
    return value

def load2(config_file):
    ruamel_yaml = YAML()
    return ruamel_yaml.load(config_file)

def save2(ostream, yaml) -> None:
    ruamel_yaml = YAML()
    ruamel_yaml.dump(yaml, ostream)

class AzureConfig:

    subscriptions = []

    def __init__(self, subscriptions):
        self.subscriptions = subscriptions

    def update_from_remote(self, credential) -> None:
        for subscription in self.subscriptions:
            subscription.update_from_remote(credential)

    def compare_with_remote(self, credential, output) -> None:
        for subscription in self.subscriptions:
            subscription.compare_with_remote(credential, output)

    def push(self, credential) -> None:
        for subscription in self.subscriptions:
            subscription.push(credential)

    def as_yaml(self):
        return [ {
                    "cloud": azure_yaml.AZURE,
                    azure_yaml.YAML_SUBSCRIPTION_LIST: [ subscription.as_yaml() for subscription in self.subscriptions]
                 } ]


def save_yaml(yaml, ostream) -> None:
    ruamel_yaml = YAML()
    ruamel_yaml.dump(yaml, ostream)

def new_azure_config(subscription_id: str) -> AzureConfig:
    output_yaml=f"""\
- cloud: {azure_yaml.AZURE}
  subscriptions:
  - {azure_yaml.YAML_SUBSCRIPTION_ID}: {subscription_id}
"""
    return load_yaml(output_yaml)

def load_yaml(source) -> AzureConfig:
    ruamel_yaml = YAML()
    yaml = ruamel_yaml.load(source)

    not_supported_providers = {provider.get("cloud","") for provider in yaml if provider.get("cloud","") not in SUPPORTED_PROVIDERS }
    for not_supported in not_supported_providers:
        logging.warning(f"Cloud provider '{not_supported}' is not supported")

    azure_providers = [provider for provider in yaml if azure_yaml.AZURE == provider.get("cloud","")]
    if len(azure_providers) == 0:
        raise ValueError("Missing Azure tenant")

    if len(azure_providers) > 1:
        raise ValueError("More than one Azure tenant defined, only one expected!")

    azure_cloud = azure_providers[0]

    assert azure_cloud[azure_yaml.YAML_SUBSCRIPTION_LIST], f"Missing '{azure_yaml.YAML_SUBSCRIPTION_LIST}' under azure cloud configuration"

    return AzureConfig(list(map(load_subscription, azure_cloud[azure_yaml.YAML_SUBSCRIPTION_LIST])))

def load_resource_group_from_yaml(name, resource_group_yaml):
    assert name, "Missing resource group name"
    assert resource_group_yaml, f"Missing YAML definition for resource group {name}"
    assert azure_yaml.YAML_AZURE_RESOURCE_LOCATION in resource_group_yaml, f"Missing resource group location for resource group {name}"

    resource_group = ResourceGroup(name, resource_group_yaml[azure_yaml.YAML_AZURE_RESOURCE_LOCATION])

    if azure_yaml.YAML_RESOURCES in resource_group_yaml:
        resources_yaml = resource_group_yaml[azure_yaml.YAML_RESOURCES]
        assert isinstance(resources_yaml, dict), "Expecting dict of resources yaml definitions"
        for name, resource_yaml in resources_yaml.items():
            resource_group.add_resource(load_resource_from_yaml(name, resource_yaml))


    return resource_group



class ResourceGroup:

    name = None
    resources = {}
    location = None

    def __init__(self, name, location):
        self.name = name
        self.resources = {}
        self.location = location

    def add_resource(self, azure_resource):
        self.resources[azure_resource.name] = azure_resource

    def as_yaml(self):
        return { azure_yaml.YAML_AZURE_RESOURCE_LOCATION: self.location, azure_yaml.YAML_RESOURCES: { name: resource.as_yaml() for name, resource in self.resources.items()} }

    def push(self, credentials, subscription_id) -> None:
        cloud.azure.api.update_resource_group(credentials, subscription_id, self.name, resource_group={
            azure_yaml.YAML_AZURE_RESOURCE_LOCATION: self.location
        })

    def __str__(self):
        return self.name

class Resource:

    name = None
    azure_resource = None

    def __init__(self, name, azure_resource):
        self.name = name
        self.azure_resource = azure_resource

    def __str__(self):
        return self.name

    def as_yaml(self):
        return azure_resource_as_yaml(self.azure_resource)

def load_resource_from_yaml(name, resource_yaml) -> Resource:
    return Resource(name, resource_yaml)

def azure_resource_as_yaml(azure_resource) -> dict:
    return azure_resource

class AzureSubscription:

    id = None
    resource_groups = {}

    def __init__(self, yaml_subscription):
        self.id = yaml_subscription[azure_yaml.YAML_SUBSCRIPTION_ID]
        self.resource_groups = {}

    def as_yaml(self) -> dict:
        return {azure_yaml.YAML_SUBSCRIPTION_ID: self.id,
                azure_yaml.YAML_RESOURCE_GROUPS :  { resource_group_name: resource_group.as_yaml() for resource_group_name, resource_group in self.resource_groups.items() }}

    def add_resource_group(self, resource_group):
        self.resource_groups[resource_group.name] = resource_group

    def update_from_remote(self, credentials, get_resources = cloud.azure.api.get_resources) -> None:

        for remote_resource_group_name, remote_resource_dict in get_resources(credentials, self.id).items():
            resource_group = ResourceGroup(remote_resource_group_name, remote_resource_dict[azure_yaml.YAML_AZURE_RESOURCE_LOCATION])
            self.add_resource_group(resource_group)
            if azure_yaml.YAML_RESOURCES in remote_resource_dict:
                resources_dict = remote_resource_dict[azure_yaml.YAML_RESOURCES]
                for resource_name, resource_dict in resources_dict.items():
                    resource = Resource(resource_name, resource_dict)
                    resource_group.add_resource(resource)

    def push(self, credentials) -> None:
        remote_resources = cloud.azure.api.get_resources(credentials, self.id)

        local_keys = self.resource_groups.keys()
        remote_keys = remote_resources.keys()
        common = local_keys & remote_keys
        only_locals = local_keys ^ common

        only_remotes = remote_keys ^ common

        for only_local in only_locals:
            self.resource_groups[only_local].push(credentials, self.id)

        for only_remote in only_remotes:
            cloud.azure.api.delete_resource_group(credentials, self.id, only_remote)



    def compare_with_remote(self, credentials, output, get_resources = cloud.azure.api.get_resources):

        remote_resources = get_resources(credentials, self.id)
        output.echo(f"Azure subscription '{self.id}'")

        local_keys = self.resource_groups.keys()
        remote_keys = remote_resources.keys()
        common = local_keys & remote_keys
        only_local = local_keys ^ common

        only_remote = remote_keys ^ common

        diff_list = []
        for only_local_resource_group in only_local:
            diff_list.append([ only_local_resource_group, "", ""])

        for common_resource_group in common:
            diff_list.append([ "", common_resource_group, ""])

        for only_remote_resource_group in only_remote:
            diff_list.append([ "", "", only_remote_resource_group])



        if only_local or only_remote:
            output.echo(f"There are differences:\n")
            print(tabulate(diff_list, headers=["Only local", "Common", "Only remote"]))
        else:
            output.echo("No changes")


    def __repr__(self):
        return id

    def __str__(self):
        return self.id


def load_subscription(subscription_yaml) -> AzureSubscription:

    azure_subscription = AzureSubscription(subscription_yaml)

    if azure_yaml.YAML_RESOURCE_GROUPS in subscription_yaml:
        resource_groups_yaml = subscription_yaml[azure_yaml.YAML_RESOURCE_GROUPS]
        assert isinstance(resource_groups_yaml, dict), "Expecting dict of resource groups yaml definitions"

        for name, resource_group_yaml in resource_groups_yaml.items():
            azure_subscription.add_resource_group(load_resource_group_from_yaml(name, resource_group_yaml))

    return azure_subscription
