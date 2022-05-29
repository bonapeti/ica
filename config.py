import logging
from ruamel.yaml import YAML
from azure_api import get_resources

AZURE="azure"
YAML_SUBSCRIPTION_ID="id"
YAML_SUBSCRIPTION_LIST="subscriptions"
YAML_RESOURCES_LIST="resources"
YAML_RESOURCE_GROUP_LIST="resourceGroups"
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

    def update_from_remote(self, credential):
        for subscription in self.subscriptions:
            subscription.update_from_remote(credential)

    def compare_with_remote(self, credential, output):
        for subscription in self.subscriptions:
            subscription.compare_with_remote(credential, output)

    def as_yaml(self):
        return [ {
                    "cloud": AZURE, 
                    YAML_SUBSCRIPTION_LIST: [ subscription.as_yaml() for subscription in self.subscriptions] 
                 } ]
    

def save_yaml(yaml, ostream):
    ruamel_yaml = YAML()
    ruamel_yaml.dump(yaml, ostream)

def new_azure_config(subscription_id):
    output_yaml=f"""\
- cloud: {AZURE}
  subscriptions:
  - {YAML_SUBSCRIPTION_ID}: {subscription_id}
"""
    return load_yaml(output_yaml)

def load_yaml(source):
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
    
    return AzureConfig(list(map(lambda subscription_yaml: AzureSubscription(subscription_yaml), azure_cloud[YAML_SUBSCRIPTION_LIST])))

class ResourceGroup:

    name = None
    resources = {}

    def __init__(self, name):
        self.name = name
        self.resources = {}

    def add_resource(self, azure_resource):
        self.resources[azure_resource.name] = Resource(azure_resource)

    def as_yaml(self):
        return { YAML_RESOURCES_LIST: [ resource.as_yaml() for name, resource in self.resources.items()]}

    def resource_count(self):
        return len(self.resources)

    def __str__(self):
        return self.name

class Resource:

    azure_resource = None

    def __init__(self, azure_resource):
        self.azure_resource = azure_resource

    def as_yaml(self):
        local_resource = { 
            YAML_AZURE_RESOURCE_NAME: self.azure_resource.name, 
            YAML_AZURE_RESOURCE_TYPE: self.azure_resource.type }
        local_resource["location"] = self.azure_resource.location
        if self.azure_resource.kind:
            local_resource["kind"] = self.azure_resource.kind
        if self.azure_resource.managed_by:
            local_resource["managed_by"] = self.azure_resource.managed_by
        if self.azure_resource.tags:
            local_resource["tags"] = self.azure_resource.tags
        return local_resource
    

    def __str__(self):
        return self.name

class AzureSubscription:

    id = None
    resource_groups = {}

    def __init__(self, yaml_subscription):
        self.id = yaml_subscription[YAML_SUBSCRIPTION_ID]
        self.resource_groups = {}

    def as_yaml(self):
        return {YAML_SUBSCRIPTION_ID: self.id,
                YAML_RESOURCE_GROUP_LIST :  { resource_group_name: resource_group.as_yaml() for resource_group_name, resource_group in self.resource_groups.items() }}

    def add_resource_group(self, new_resource_group_name):
        self.resource_groups[new_resource_group_name] = ResourceGroup(new_resource_group_name)
            
    def update_from_remote(self, credentials, get_resources = get_resources):

        for remote_resource_group_name, remote_resource_list in get_resources(credentials, self.id).items():
            self.add_resource_group(remote_resource_group_name)
            for resource in remote_resource_list:
                self.resource_groups[remote_resource_group_name].add_resource(resource)

    def compare_with_remote(self, credentials, output, get_resources = get_resources):

        remote_resource_group_count = 0
        remote_resource_count = 0
        for remote_resource_group_name, remote_resource_list in get_resources(credentials, self.id).items():
            remote_resource_group_count = remote_resource_group_count + 1
            remote_resource_count = remote_resource_count + len(remote_resource_list)
        output.echo(f"Azure subscription '{self.id}'")
        (local_resource_group_count, local_resource_count) = self.__local_resources_count()
        if (remote_resource_group_count, remote_resource_count) == (local_resource_group_count, local_resource_count):
            output.echo("\tNo changes")
        else:
            output.echo(f"\tThere are differences. Local: {local_resource_group_count}, remote: {remote_resource_count}")

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






        