from azure.mgmt.resource import resources, subscriptions
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
        if len(azure_providers) == 0:
            raise ValueError("Missing Azure tenant")

        if len(azure_providers) > 1:
            raise ValueError("More than one Azure tenant defined, only one expected!")
        
        azure_tenant = azure_providers[0]
        assert type(azure_tenant) == dict

        tenant_id = expect_string(azure_tenant,YAML_TENANT_ID, "Missing tenant ID!")
        tenant_name = expect_string(azure_tenant,YAML_TENANT_NAME, "Missing tenant name!")

        assert azure_tenant["subscriptions"], "Missing 'subscriptions' under azure cloud configuration"
        assert type(azure_tenant["subscriptions"]) == list

        subscriptions_configs = list(map(lambda subscription: AzureSubscription(subscription["id"],subscription["name"]), azure_tenant["subscriptions"]))
        assert type(subscriptions_configs) == list

        azure_config = AzureConfig(tenant_id, tenant_name, subscriptions_configs)
        return Config(azure_config)

    


class AzureConfig:

    id = None
    name = None
    subscriptions = []
    

    def __init__(self, id, name, subscriptions):
        self.id = id
        self.name = name
        self.subscriptions = subscriptions

    def __repr__(self):
        return f"Azure(tenantId='{self.id}')"
    
class AzureSubscription:

    id = None
    name = None
    resources = []

    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __repr__(self):
        return id

    def __str__(self):
        return self.name if self.name else self.id
