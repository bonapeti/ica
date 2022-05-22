import config 
import io
import pytest

TENANT_ID="900a843e-af52-4bc8-9009-4676366d9d97"
TEST_SUBSCRIPTION_ID="5ed44b1f-1379-4af2-b7c5-097bbd2e2ee2"
TEST_LOCATION_NORTH_EUROPE = "northeurope"
TEST_RESOURCE_GROUP = "test_resource_group"
ANOTHER_RESOURCE_GROUP = "AnotherResourceGroup"

TEST_YAML=f"""\
- cloud: azure
  subscriptions:
  - id: {TEST_SUBSCRIPTION_ID}
"""

def test_not_supported_provider(cli_runner):
    with pytest.raises(ValueError):
        config.load_yaml(f"""\
- cloud: unknown_cloud
""")

def test_load_azure_subscription_from_valid_yaml(cli_runner):
    azure_config = config.load_yaml(TEST_YAML)
    
    assert len(azure_config.subscriptions) == 1

    subscription = azure_config.subscriptions[0]
    assert subscription.id == TEST_SUBSCRIPTION_ID
     

def test_azure_config_as_yaml(cli_runner):
    azure_config = config.AzureConfig([])
    assert [ {"cloud":config.AZURE, config.YAML_SUBSCRIPTION_LIST: []}] == azure_config.as_yaml()


def test_empty_subscription_as_yaml(cli_runner):
    subscription = config.AzureSubscription({config.YAML_SUBSCRIPTION_ID: "id"})
    result = subscription.as_yaml()
    assert { config.YAML_SUBSCRIPTION_ID: "id",
               config.YAML_RESOURCE_GROUP_LIST: []} == result



class MockAzureResource:
    name =  "AzureResource"
    type = "AzureResourceType"
    tags = { "name": "value"}
    location = TEST_LOCATION_NORTH_EUROPE
    kind = None
    identity = None
    managed_by = None
   
    resource_group_name = TEST_RESOURCE_GROUP

class MockAzureResourceGroup:
  name = TEST_RESOURCE_GROUP

class MockClick:
  test_output = io.StringIO()

  def echo(self, message):
    self.test_output.write(message)

  def get_content(self):
    return self.test_output.getvalue()

def test_azure_resource_as_yaml(cli_runner):
   azure_resource = config.Resource(MockAzureResource())
   assert azure_resource.as_yaml() == {
                        config.YAML_AZURE_RESOURCE_LOCATION: TEST_LOCATION_NORTH_EUROPE,
                        config.YAML_AZURE_RESOURCE_NAME: MockAzureResource.name,
                        config.YAML_AZURE_RESOURCE_TYPE: MockAzureResource.type,
                        config.YAML_AZURE_RESOURCE_TAGS: MockAzureResource.tags }

def test_empty_azure_resource_group_as_yaml(cli_runner):
   azure_resource_group = config.ResourceGroup(TEST_RESOURCE_GROUP)
   assert azure_resource_group.as_yaml() == {
                        TEST_RESOURCE_GROUP: { config.YAML_RESOURCES_LIST:[] }}

def test_azure_resource_group_with_resource_as_yaml(cli_runner):
   azure_resource_group = config.ResourceGroup(TEST_RESOURCE_GROUP)
   azure_resource_group.add_resource(MockAzureResource())
   assert azure_resource_group.as_yaml() == {
                        TEST_RESOURCE_GROUP: { config.YAML_RESOURCES_LIST: [
                          {
                            config.YAML_AZURE_RESOURCE_LOCATION: TEST_LOCATION_NORTH_EUROPE,
                            config.YAML_AZURE_RESOURCE_NAME: MockAzureResource.name,
                            config.YAML_AZURE_RESOURCE_TYPE: MockAzureResource.type,
                            config.YAML_AZURE_RESOURCE_TAGS: MockAzureResource.tags 
                            }
                        ]} }


def test_update_subscription_from_remote():

    resource = MockAzureResource()

    def mock_get_resources(credentials, subscription_id):
      return { TEST_RESOURCE_GROUP: [ resource], ANOTHER_RESOURCE_GROUP: [] }

    subscription = config.AzureSubscription({ config.YAML_SUBSCRIPTION_ID: TEST_SUBSCRIPTION_ID })
    subscription.update_from_remote(None, mock_get_resources)
    
    assert subscription.as_yaml() == { config.YAML_SUBSCRIPTION_ID: TEST_SUBSCRIPTION_ID,
             config.YAML_RESOURCE_GROUP_LIST:
                {
                  TEST_RESOURCE_GROUP:
                  {
                    config.YAML_RESOURCES_LIST: 
                    [ 
                        { 
                          config.YAML_AZURE_RESOURCE_NAME: MockAzureResource.name, 
                          config.YAML_AZURE_RESOURCE_TYPE: MockAzureResource.type,
                          config.YAML_AZURE_RESOURCE_LOCATION: MockAzureResource.location,
                          config.YAML_AZURE_RESOURCE_TAGS:  MockAzureResource.tags
                        }
                    ]
                  }, 
                  ANOTHER_RESOURCE_GROUP:
                  {
                    config.YAML_RESOURCES_LIST: 
                    []
                  }
                }
            }

def test_compare_subscription_with_1_remote_resource():

    resource = MockAzureResource()

    def mock_get_resources(credentials, subscription_id):
      return { TEST_RESOURCE_GROUP: [ resource] }

    subscription = config.AzureSubscription({ config.YAML_SUBSCRIPTION_ID: TEST_SUBSCRIPTION_ID })
    mock_click = MockClick()
    
    subscription.compare_with_remote(None, mock_click, mock_get_resources)

    assert mock_click.get_content() == f"Azure subscription '{TEST_SUBSCRIPTION_ID}'\tThere are differences. Local: 0, remote: 1"
