from azure.mgmt.resource import resources, subscriptions
from ruamel.yaml import YAML
import sys

AZURE="azure"
YAML_TENANT_ID="tenantId"
YAML_TENANT_NAME="name"

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
    def load(source):
        yaml = YAML()
        #yaml.preserve_quotes = True
        yaml_config = yaml.load(source)
        
        azure_providers = [provider for provider in yaml_config if AZURE == provider.get("cloud","")]
        if len(azure_providers) == 0:
            raise ValueError("Missing Azure tenant")

        if len(azure_providers) > 1:
            raise ValueError("More than one Azure tenant defined, only one expected!")
        
        azure_tenant = azure_providers[0]
        
        expect_string(azure_tenant,YAML_TENANT_ID, "Missing tenant ID!")
        expect_string(azure_tenant,YAML_TENANT_NAME, "Missing tenant name!")

        assert azure_tenant["subscriptions"], "Missing 'subscriptions' under azure cloud configuration"
        
        azure_config = AzureConfig(azure_tenant)
        return Config(yaml, yaml_config, azure_config)

    def save(self, newfile_path):
        with open(newfile_path, 'w') as file:
            self.yaml.dump(self.yaml_config, file)

    def dump(self):
        self.yaml.dump(self.yaml_config, sys.stdout)
        


class AzureConfig:

    id = None
    name = None
    subscriptions = []
    yaml_config = None

    def __init__(self, azure_yaml):
        self.id = azure_yaml[YAML_TENANT_ID]
        self.name = azure_yaml[YAML_TENANT_NAME]
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
        self.yaml_config["resources"] = []

    def get_resources(self):
        if self.yaml_config["resources"] is None:
            self.yaml_config["resources"] = []
        return self.yaml_config["resources"]

    def add_resource(self, new_resource):
        self.get_resources().append(new_resource)

    def local_resource_count(self):
        return len(self.yaml_config.get("resources",[]))


    def __repr__(self):
        return id

    def __str__(self):
        return self.name if self.name else self.id
