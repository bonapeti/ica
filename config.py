from azure.mgmt.resource import ResourceManagementClient
from ruamel.yaml import YAML


AZURE="azure"
YAML_TENANT_ID="tenantId"
YAML_SUBSCRIPTION_ID="id"
YAML_SUBSCRIPTION_NAME="name"
YAML_SUBSCRIPTION_LIST="subscriptions"
YAML_RESOURCES_LIST="resources"
YAML_AZURE_RESOURCE_NAME="name"
YAML_AZURE_RESOURCE_TYPE="type"

SUPPORTED_PROVIDERS=[AZURE]

def expect_string(dict_var, name, error_message):
    value = dict_var.get(name)
    if value is None:
        raise ValueError(error_message)
    assert type(value) == str
    return value

class Config:

    yaml_config = None
    azure = None
    

    def __init__(self, yaml_config, azure):
        self.yaml_config = yaml_config
        self.azure = azure

    def __repr__(self):
        return f"Config('{self.azure}')"

def new_azure_config(tenant_id, subscription_id, subscription_name):
    output_yaml=f"""\
- cloud: {AZURE}
  {YAML_TENANT_ID}: {tenant_id}
  subscriptions:
  - {YAML_SUBSCRIPTION_ID}: {subscription_id}
    {YAML_SUBSCRIPTION_NAME}: {subscription_name}
"""
    return load_yaml(output_yaml)

def load_yaml(source):
    yaml = YAML()
    yaml_config = yaml.load(source)
    
    not_supported_providers = {provider.get("cloud","") for provider in yaml_config if provider.get("cloud","") not in SUPPORTED_PROVIDERS }
    for not_supported in not_supported_providers:
        print(f"Cloud provider '{not_supported}' is not supported")

    azure_providers = [provider for provider in yaml_config if AZURE == provider.get("cloud","")]
    if len(azure_providers) == 0:
        raise ValueError("Missing Azure tenant")

    if len(azure_providers) > 1:
        raise ValueError("More than one Azure tenant defined, only one expected!")
    
    azure_tenant = azure_providers[0]
    
    expect_string(azure_tenant,YAML_TENANT_ID, "Missing tenant ID!")

    assert azure_tenant[YAML_SUBSCRIPTION_LIST], f"Missing '{YAML_SUBSCRIPTION_LIST}' under azure cloud configuration"
    
    azure_config = AzureTenant(azure_tenant)
    return Config(yaml_config, azure_config)

def save_yaml(yaml_config, ostream):
    yaml = YAML()
    yaml.dump(yaml_config, ostream)

class AzureTenant:

    id = None
    subscriptions = []
    yaml_config = None

    def __init__(self, azure_yaml):
        self.id = azure_yaml[YAML_TENANT_ID]
        self.yaml_config = azure_yaml
        self.subscriptions = list(map(lambda subscription_yaml: AzureSubscription(subscription_yaml), azure_yaml["subscriptions"]))

    def __repr__(self):
        return f"Azure(tenantId='{self.id}')"
    
class AzureSubscription:

    id = None
    name = None
    yaml_config = None

    def __init__(self, yaml_subscription):
        self.id = yaml_subscription[YAML_SUBSCRIPTION_ID]
        self.name = yaml_subscription[YAML_SUBSCRIPTION_NAME]
        self.yaml_config = yaml_subscription

    def add_resource(self, new_resource):
        if not YAML_RESOURCES_LIST in self.yaml_config:
            self.yaml_config[YAML_RESOURCES_LIST] = []
        self.yaml_config[YAML_RESOURCES_LIST].append(new_resource)

    def local_resource_count(self):
        return len(self.yaml_config.get(YAML_RESOURCES_LIST,[]))


    def __repr__(self):
        return id

    def __str__(self):
        return self.name if self.name else self.id

def __get_resources_from_azure(credentials, subscription_id):
    assert subscription_id, "Missing subscription ID"

    with ResourceManagementClient(credentials, subscription_id) as resource_client:
        return list(resource_client.resources.list(expand="createdTime,changedTime,provisioningState"))

def update_tenant_from_remote(credential, tenant):
    for subscription in tenant.subscriptions:
        update_subscription_from_remote(credential, subscription)

def compare_tenant_with_remote(credential, tenant, output):
    for subscription in tenant.subscriptions:
        compare_subscription_with_remote(credential, subscription, output)

def update_subscription_from_remote(credentials, subscription, get_resources = __get_resources_from_azure):

    for resource in get_resources(credentials, subscription.id):
        local_resource = { YAML_AZURE_RESOURCE_NAME: resource.name, YAML_AZURE_RESOURCE_TYPE: resource.type }
        local_resource["location"] = resource.location
        if resource.kind:
            local_resource["kind"] = resource.kind
        if resource.managed_by:
            local_resource["managed_by"] = resource.managed_by
        if resource.identity:
            local_resource["identity"] = resource.identity
        if resource.tags:
            local_resource["tags"] = resource.tags
        if resource.properties:
            local_resource["properties"] = resource.properties
        subscription.add_resource(local_resource)




def compare_subscription_with_remote(credentials, subscription, output, get_resources = __get_resources_from_azure):

    remote_resources = get_resources(credentials, subscription.id)
    output.echo(f"Azure subscription '{subscription.name}'")
    if len(remote_resources) == subscription.local_resource_count():
        output.echo("\tNo changes")
    else:
        output.echo("\tThere are differences")


        