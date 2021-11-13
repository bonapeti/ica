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

    yaml_config = None
    subscriptions = []

    def __init__(self, yaml_config, subscriptions):
        self.yaml_config = yaml_config
        self.subscriptions = subscriptions

    def __repr__(self):
        return f"Config('{self.azure}')"

    def update_from_remote(self, credential):
        for subscription in self.subscriptions:
            subscription.update_from_remote(credential)

    def compare_with_remote(self, credential, output):
        for subscription in self.subscriptions:
            subscription.compare_with_remote(credential, output)

    def save_yaml(self, ostream):
        ruamel_yaml = YAML()
        ruamel_yaml.dump(self.yaml_config, ostream)

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
        print(f"Cloud provider '{not_supported}' is not supported")

    azure_providers = [provider for provider in yaml if AZURE == provider.get("cloud","")]
    if len(azure_providers) == 0:
        raise ValueError("Missing Azure tenant")

    if len(azure_providers) > 1:
        raise ValueError("More than one Azure tenant defined, only one expected!")
    
    azure_cloud = azure_providers[0]
    
    assert azure_cloud[YAML_SUBSCRIPTION_LIST], f"Missing '{YAML_SUBSCRIPTION_LIST}' under azure cloud configuration"
    
    return AzureConfig(yaml, list(map(lambda subscription_yaml: AzureSubscription(subscription_yaml), azure_cloud[YAML_SUBSCRIPTION_LIST])))



class AzureSubscription:

    id = None
    yaml_config = None

    def __init__(self, yaml_subscription):
        self.id = yaml_subscription[YAML_SUBSCRIPTION_ID]
        self.yaml_config = yaml_subscription

    def add_resource_group(self, new_resource_group_name):
        if not YAML_RESOURCE_GROUP_LIST in self.yaml_config:
            self.yaml_config[YAML_RESOURCE_GROUP_LIST] = {  }
        logging.debug(f"Adding resource group {new_resource_group_name}")
        self.yaml_config[YAML_RESOURCE_GROUP_LIST][new_resource_group_name]={ YAML_RESOURCES_LIST: [] }

    def add_resource(self, new_resource_group_name, new_resource):
        self.yaml_config[YAML_RESOURCE_GROUP_LIST][new_resource_group_name][YAML_RESOURCES_LIST].append(new_resource)

    def update_from_remote(self, credentials, get_resources = get_resources):

        for remote_resource_group_name, remote_resource_list in get_resources(credentials, self.id).items():
            self.add_resource_group(remote_resource_group_name)
            for resource in remote_resource_list:
                local_resource = self.__convert_resource_to_local(resource)
                self.add_resource(remote_resource_group_name, local_resource)

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
            output.echo(f"\tThere are differences. Local: {local_resource_count}, remote: {remote_resource_count}")

    def __convert_resource_to_local(self, resource):
        local_resource = { YAML_AZURE_RESOURCE_NAME: resource.name, YAML_AZURE_RESOURCE_TYPE: resource.type }
        local_resource["location"] = resource.location
        if resource.kind:
            local_resource["kind"] = resource.kind
        if resource.managed_by:
            local_resource["managed_by"] = resource.managed_by
        if resource.tags:
            local_resource["tags"] = resource.tags
        return local_resource

    def __local_resources_count(self):
        """Returns the number of resource groups and resources in local config file as tuple"""

        local_resource_groups_count = 0
        local_resource_count = 0
        local_resource_groups = {}
        if YAML_RESOURCE_GROUP_LIST in self.yaml_config:
            local_resource_groups = self.yaml_config[YAML_RESOURCE_GROUP_LIST]

        for resource_group_name, local_resource_map in local_resource_groups.items():
            local_resource_groups_count = local_resource_groups_count + 1
            local_resource_count = local_resource_count + len(local_resource_map[YAML_RESOURCES_LIST])
        return local_resource_groups_count, local_resource_count


    def __repr__(self):
        return id

    def __str__(self):
        return self.id






        