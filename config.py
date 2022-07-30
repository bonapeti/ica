import logging
from ruamel.yaml import YAML
from azure_api import get_resources
from tabulate import tabulate

AZURE="azure"
YAML_SUBSCRIPTION_ID="id"
YAML_SUBSCRIPTION_LIST="subscriptions"
YAML_RESOURCES="resources"
YAML_RESOURCE_GROUPS="resourceGroups"
YAML_AZURE_RESOURCE_NAME="name"
YAML_AZURE_RESOURCE_TYPE="type"
YAML_AZURE_RESOURCE_LOCATION="location"
YAML_AZURE_RESOURCE_TAGS="tags"

SUPPORTED_PROVIDERS=[AZURE]

def expect_string(dict_var, name, error_message):
    value = dict_var.get(name)
    if value is None:
        raise ValueError(error_message)
    assert type(value) == str
    return value

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

    def as_yaml(self) -> list[dict]:
        return [ {
                    "cloud": AZURE, 
                    YAML_SUBSCRIPTION_LIST: [ subscription.as_yaml() for subscription in self.subscriptions] 
                 } ]
    

def save_yaml(yaml, ostream) -> None:
    ruamel_yaml = YAML()
    ruamel_yaml.dump(yaml, ostream)

def new_azure_config(subscription_id: str) -> AzureConfig:
    output_yaml=f"""\
- cloud: {AZURE}
  subscriptions:
  - {YAML_SUBSCRIPTION_ID}: {subscription_id}
"""
    return load_yaml(output_yaml)

def load_yaml(source) -> AzureConfig:
    ruamel_yaml = YAML()
    yaml = ruamel_yaml.load(source)
    
    not_supported_providers = {provider.get("cloud","") for provider in yaml if provider.get("cloud","") not in SUPPORTED_PROVIDERS }
    for not_supported in not_supported_providers:
        logging.warning(f"Cloud provider '{not_supported}' is not supported")

    azure_providers = [provider for provider in yaml if AZURE == provider.get("cloud","")]
    if len(azure_providers) == 0:
        raise ValueError("Missing Azure tenant")

    if len(azure_providers) > 1:
        raise ValueError("More than one Azure tenant defined, only one expected!")
    
    azure_cloud = azure_providers[0]
    
    assert azure_cloud[YAML_SUBSCRIPTION_LIST], f"Missing '{YAML_SUBSCRIPTION_LIST}' under azure cloud configuration"
    
    return AzureConfig(list(map(load_subscription, azure_cloud[YAML_SUBSCRIPTION_LIST])))

def load_resource_group(name, resource_group_yaml):
    resource_group = ResourceGroup(name)

    if YAML_RESOURCES in resource_group_yaml:
        resources_yaml = resource_group_yaml[YAML_RESOURCES]
        assert isinstance(resources_yaml, dict), "Expecting dict of resources yaml definitions"
        for name, resource_yaml in resources_yaml.items():
            resource_group.add_resource(load_resource(name, resource_yaml))


    return resource_group



class ResourceGroup:

    name = None
    resources = {}

    def __init__(self, name):
        self.name = name
        self.resources = {}

    def add_resource(self, azure_resource):
        self.resources[azure_resource.name] = azure_resource

    def as_yaml(self):
        return { YAML_RESOURCES: { name: resource_as_yaml(resource) for name, resource in self.resources.items()} }

    def resource_count(self) -> int:
        return len(self.resources)

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

def load_resource(name, resource_yaml) -> Resource:
    return Resource(name, resource_yaml)

def resource_as_yaml(azure_resource) -> dict:
    local_resource = { YAML_AZURE_RESOURCE_TYPE: azure_resource.type }
    local_resource["location"] = azure_resource.location
    if azure_resource.kind:
        local_resource["kind"] = azure_resource.kind
    if azure_resource.managed_by:
        local_resource["managed_by"] = azure_resource.managed_by
    if azure_resource.tags:
        local_resource["tags"] = azure_resource.tags
    return local_resource

class AzureSubscription:

    id = None
    resource_groups = {}

    def __init__(self, yaml_subscription):
        self.id = yaml_subscription[YAML_SUBSCRIPTION_ID]
        self.resource_groups = {}

    def as_yaml(self) -> dict:
        return {YAML_SUBSCRIPTION_ID: self.id,
                YAML_RESOURCE_GROUPS :  { resource_group_name: resource_group.as_yaml() for resource_group_name, resource_group in self.resource_groups.items() }}

    def add_resource_group(self, resource_group):
        self.resource_groups[resource_group.name] = resource_group
            
    def update_from_remote(self, credentials, get_resources = get_resources) -> None:

        for remote_resource_group_name, remote_resource_list in get_resources(credentials, self.id).items():
            resource_group = ResourceGroup(remote_resource_group_name)
            self.add_resource_group(resource_group)
            for resource in remote_resource_list:
                resource_group.add_resource(resource)

    def compare_with_remote(self, credentials, output, get_resources = get_resources):

        remote_resource_group_count = 0
        remote_resource_count = 0
        remote_resources = get_resources(credentials, self.id)
        for remote_resource_group_name, remote_resource_list in remote_resources.items():
            remote_resource_group_count = remote_resource_group_count + 1
            remote_resource_count = remote_resource_count + len(remote_resource_list)
        output.echo(f"Azure subscription '{self.id}'")
        (local_resource_group_count, local_resource_count) = self.__local_resources_count()

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
            

    def __local_resources_count(self):
        """Returns the number of resource groups and resources in local config file as tuple"""

        local_resource_count = 0
        for resource_group_name, resource_group in self.resource_groups.items():
            local_resource_count = local_resource_count +resource_group.resource_count()
        return len(self.resource_groups), local_resource_count


    def __repr__(self):
        return id

    def __str__(self):
        return self.id


def load_subscription(subscription_yaml) -> AzureSubscription:

    azure_subscription = AzureSubscription(subscription_yaml)

    if YAML_RESOURCE_GROUPS in subscription_yaml:
        resource_groups_yaml = subscription_yaml[YAML_RESOURCE_GROUPS]
        assert isinstance(resource_groups_yaml, dict), "Expecting dict of resource groups yaml definitions"

        for name, resource_group_yaml in resource_groups_yaml.items():
            azure_subscription.add_resource_group(load_resource_group(name, resource_group_yaml))

    return azure_subscription



        