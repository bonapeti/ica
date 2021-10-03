from azure.mgmt.resource import subscriptions
import yaml

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

    azure = None

    def __init__(self, azure):
        self.azure = azure

    def __repr__(self):
        return f"Config('{self.azure}')"

    @staticmethod
    def load(source):
        yaml_config = yaml.safe_load(source)
        assert type(yaml_config) == list

        azure_providers = [provider for provider in yaml_config if AZURE == provider.get("cloud","")]
        if len(azure_providers) > 1:
            raise ValueError("More than one Azure tenant defined, only one expected!")
        
        azure_tenant = azure_providers[0]
        assert type(azure_tenant) == dict

        tenant_id = expect_string(azure_tenant,YAML_TENANT_ID, "Missing tenant ID!")
        tenant_name = expect_string(azure_tenant,YAML_TENANT_NAME, "Missing tenant name!")

        azure_config = AzureConfig(tenant_id, tenant_name)
        return Config(azure_config)

    


class AzureConfig:

    id = None
    name = None
    subscriptions = None

    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __repr__(self):
        return f"Azure(tenantId='{self.id}')"
    