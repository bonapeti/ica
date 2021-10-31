import config 
import io
import pytest

TENANT_ID="7a9376d4-7c43-480f-82ba-a090647f651d"
SUBSCRIPTION_ID="59134732-c952-4ef9-ab63-94a75300c7dc"
SUBSCRIPTION_NAME="GlobalSolutions_Sandbox"

TEST_YAML=f"""\
- cloud: azure
  tenantId: {TENANT_ID}
  subscriptions:
  - id: {SUBSCRIPTION_ID}
    name: {SUBSCRIPTION_NAME}
"""

def test_not_supported_provider(cli_runner):
    with pytest.raises(ValueError):
        config.load_yaml(f"""\
- cloud: unknown_cloud
""")

def test_load_azure_tenant(cli_runner):
    yaml_config = config.load_yaml(TEST_YAML)
    tenant = yaml_config.azure
    
    assert tenant.id == TENANT_ID
    assert len(tenant.subscriptions) == 1
    subscription = tenant.subscriptions[0]
    assert subscription.id == SUBSCRIPTION_ID
    assert subscription.name == SUBSCRIPTION_NAME

def test_save_azure_resources(cli_runner):
    yaml_config = config.load_yaml(TEST_YAML)
    yaml_config.azure.subscriptions[0].add_resource({config.YAML_AZURE_RESOURCE_NAME: "boo", config.YAML_AZURE_RESOURCE_TYPE: "baa" })
    with io.StringIO() as test_output:
      config.save_yaml(yaml_config.yaml_config, test_output)
      expected_content = f"""\
- cloud: azure
  tenantId: {TENANT_ID}
  subscriptions:
  - id: {SUBSCRIPTION_ID}
    name: {SUBSCRIPTION_NAME}
    resources:
    - name: boo
      type: baa
"""
      assert expected_content == test_output.getvalue()

TEST_SUBSCRIPTION_ID="TEST_SUBSCRIPTION_ID"
TEST_SUBSCRIPTION_NAME="TEST_SUBSCRIPTION_NAME"

class MockAzureResource:
    name =  "AzureResource"
    type = "AzureResourceType"

def test_update_subscription_from_remote():

    resource = MockAzureResource()

    def mock_get_resources(credentials, subscription_id):
        return [ resource ]

    subscription = config.AzureSubscription({ config.YAML_SUBSCRIPTION_ID: TEST_SUBSCRIPTION_ID, config.YAML_SUBSCRIPTION_NAME: TEST_SUBSCRIPTION_NAME })
    config.update_subscription_from_remote(None, subscription, mock_get_resources)
    assert { config.YAML_SUBSCRIPTION_ID: TEST_SUBSCRIPTION_ID,
             config.YAML_SUBSCRIPTION_NAME: TEST_SUBSCRIPTION_NAME,
             config.YAML_RESOURCES: 
                 [ 
                    { 
                      config.YAML_AZURE_RESOURCE_NAME: MockAzureResource.name, 
                      config.YAML_AZURE_RESOURCE_TYPE: MockAzureResource.type 
                    }
                 ]
            
            } == subscription.yaml_config
