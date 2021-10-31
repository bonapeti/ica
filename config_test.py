import config 
import io
import pytest

TENANT_ID="900a843e-af52-4bc8-9009-4676366d9d97"
TEST_SUBSCRIPTION_ID="5ed44b1f-1379-4af2-b7c5-097bbd2e2ee2"
TEST_SUBSCRIPTION_NAME="TEST_SUBSCRIPTION_NAME"

TEST_YAML=f"""\
- cloud: azure
  tenantId: {TENANT_ID}
  subscriptions:
  - id: {TEST_SUBSCRIPTION_ID}
    name: {TEST_SUBSCRIPTION_NAME}
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
    assert subscription.id == TEST_SUBSCRIPTION_ID
    assert subscription.name == TEST_SUBSCRIPTION_NAME

def test_save_azure_resources(cli_runner):
    yaml_config = config.load_yaml(TEST_YAML)
    yaml_config.azure.subscriptions[0].add_resource({config.YAML_AZURE_RESOURCE_NAME: "boo", config.YAML_AZURE_RESOURCE_TYPE: "baa" })
    with io.StringIO() as test_output:
      config.save_yaml(yaml_config.yaml_config, test_output)
      expected_content = f"""\
- cloud: azure
  tenantId: {TENANT_ID}
  subscriptions:
  - id: {TEST_SUBSCRIPTION_ID}
    name: {TEST_SUBSCRIPTION_NAME}
    resources:
    - name: boo
      type: baa
"""
      assert expected_content == test_output.getvalue()



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
