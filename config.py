from azure.mgmt.resource import resources, subscriptions
from ruamel.yaml import YAML


AZURE="azure"
YAML_TENANT_ID="tenantId"

SUPPORTED_PROVIDERS=[AZURE]

def expect_string(dict_var, name, error_message):
    value = dict_var.get(name)
    if value is None:
        raise ValueError(error_message)
    assert type(value) == str
    return value

class Config:

    yaml = None
    yaml_config = None
    azure = None
    

    def __init__(self, yaml, yaml_config, azure):
        self.yaml = yaml
        self.yaml_config = yaml_config
        self.azure = azure

    def __repr__(self):
        return f"Config('{self.azure}')"

    @staticmethod
    def new_azure_config(tenant_id, subscription_id, subscription_name):
        output_yaml=f"""\
- cloud: azure
  tenantId: {tenant_id}
  subscriptions:
  - id: {subscription_id}
    name: {subscription_name}
"""
        return Config.load(output_yaml)

    @staticmethod
    def load(source):
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

        assert azure_tenant["subscriptions"], "Missing 'subscriptions' under azure cloud configuration"
        
        azure_config = AzureConfig(azure_tenant)
        return Config(yaml, yaml_config, azure_config)

    def save(self, ostream):
        self.yaml.dump(self.yaml_config, ostream)

   


class AzureConfig:

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
        self.id = yaml_subscription["id"]
        self.name = yaml_subscription["name"]
        self.yaml_config = yaml_subscription

    def add_resource(self, new_resource):
        if not "resources" in self.yaml_config:
            self.yaml_config["resources"] = []
        self.yaml_config["resources"].append(new_resource)

    def local_resource_count(self):
        return len(self.yaml_config.get("resources",[]))


    def __repr__(self):
        return id

    def __str__(self):
        return self.name if self.name else self.id
