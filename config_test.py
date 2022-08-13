import io
import pytest
import config
import azure_yaml

TENANT_ID="900a843e-af52-4bc8-9009-4676366d9d97"
TEST_SUBSCRIPTION_ID="5ed44b1f-1379-4af2-b7c5-097bbd2e2ee2"
TEST_LOCATION_NORTH_EUROPE = "northeurope"
TEST_RESOURCE_GROUP = "test_resource_group"
ANOTHER_RESOURCE_GROUP = "AnotherResourceGroup"

TEST_YAML=f"""\
- cloud: azure
  subscriptions:
  - id: {TEST_SUBSCRIPTION_ID}
    resourceGroups:
      NetworkWatcherRG:
        location: {TEST_LOCATION_NORTH_EUROPE}
        resources:
          NetworkWatcher_centralus:
            - type: resource_type
          NetworkWatcher_northeurope:
            - type: resource_type
      azure_devops_resources:
        location: {TEST_LOCATION_NORTH_EUROPE}
        resources: {{}}
"""

def test_not_supported_provider(cli_runner):
    with pytest.raises(ValueError):
        config.load_yaml("""\
- cloud: unknown_cloud
""")

def test_load_azure_subscription_from_valid_yaml(cli_runner):
    azure_config = config.load_yaml(TEST_YAML)

    assert len(azure_config.subscriptions) == 1

    subscription = azure_config.subscriptions[0]
    assert subscription.id == TEST_SUBSCRIPTION_ID

def test_load_resource_groups_from_valid_yaml(cli_runner):
    azure_config = config.load_yaml(TEST_YAML)

    subscription = azure_config.subscriptions[0]
    assert len(subscription.resource_groups) == 2, "Should have at least 2 resource group loaded"

def test_load_resources_from_valid_yaml(cli_runner):
    azure_config = config.load_yaml(TEST_YAML)

    subscription = azure_config.subscriptions[0]
    assert len(subscription.resource_groups["NetworkWatcherRG"].resources) == 2, "Should have at least 2 resource loaded"

def test_azure_config_as_yaml(cli_runner):
    azure_config = config.AzureConfig([])
    assert [ {"cloud":azure_yaml.AZURE, azure_yaml.YAML_SUBSCRIPTION_LIST: []}] == azure_config.as_yaml()


def test_empty_subscription_as_yaml(cli_runner):
    subscription = config.AzureSubscription({azure_yaml.YAML_SUBSCRIPTION_ID: "id"})
    result = subscription.as_yaml()
    assert { azure_yaml.YAML_SUBSCRIPTION_ID: "id",
               azure_yaml.YAML_RESOURCE_GROUPS: {}} == result



class MockAzureResource:
    name =  "AzureResource"
    type = "AzureResourceType"
    tags = { "name": "value"}
    location = TEST_LOCATION_NORTH_EUROPE
    kind = None
    identity = None
    managed_by = None
    resource_group_name = TEST_RESOURCE_GROUP
    yaml = "MockResourceYaml"

    def as_yaml(self):
        return self.yaml

class MockAzureResourceGroup:
    name = TEST_RESOURCE_GROUP

class MockClick:
    test_output = io.StringIO()

    def echo(self, message):
        self.test_output.write(message)
        self.test_output.write("\n")

    def get_content(self):
        return self.test_output.getvalue()

def test_azure_resource_as_yaml(cli_runner):
    azure_resource = MockAzureResource()
    assert config.azure_resource_as_yaml({
                        azure_yaml.YAML_AZURE_RESOURCE_LOCATION: TEST_LOCATION_NORTH_EUROPE,
                        azure_yaml.YAML_AZURE_RESOURCE_TYPE: MockAzureResource.type,
                        azure_yaml.YAML_AZURE_RESOURCE_TAGS: MockAzureResource.tags }) == {
                        azure_yaml.YAML_AZURE_RESOURCE_LOCATION: TEST_LOCATION_NORTH_EUROPE,
                        azure_yaml.YAML_AZURE_RESOURCE_TYPE: MockAzureResource.type,
                        azure_yaml.YAML_AZURE_RESOURCE_TAGS: MockAzureResource.tags }

def test_empty_azure_resource_group_as_yaml(cli_runner):
    azure_resource_group = config.ResourceGroup(TEST_RESOURCE_GROUP, TEST_LOCATION_NORTH_EUROPE )
    assert azure_resource_group.as_yaml() == { azure_yaml.YAML_AZURE_RESOURCE_LOCATION: TEST_LOCATION_NORTH_EUROPE,
                                                azure_yaml.YAML_RESOURCES: {} }

def test_azure_resource_group_with_resource_as_yaml(cli_runner):
    azure_resource_group = config.ResourceGroup(TEST_RESOURCE_GROUP, TEST_LOCATION_NORTH_EUROPE)
    resource = MockAzureResource()
    azure_resource_group.add_resource(resource)
    assert azure_resource_group.as_yaml() == { azure_yaml.YAML_AZURE_RESOURCE_LOCATION: TEST_LOCATION_NORTH_EUROPE,
                                                azure_yaml.YAML_RESOURCES: {
                                                MockAzureResource.name: MockAzureResource.yaml
                                            }}


def test_update_subscription_from_remote():

    resource = MockAzureResource()

    def mock_get_resources(credentials, subscription_id):
        return { TEST_RESOURCE_GROUP: { azure_yaml.YAML_AZURE_RESOURCE_LOCATION: TEST_LOCATION_NORTH_EUROPE,  azure_yaml.YAML_RESOURCES: { MockAzureResource.name: {  }} },
                ANOTHER_RESOURCE_GROUP: {azure_yaml.YAML_AZURE_RESOURCE_LOCATION: TEST_LOCATION_NORTH_EUROPE,  azure_yaml.YAML_RESOURCES: {} }}

    subscription = config.AzureSubscription({ azure_yaml.YAML_SUBSCRIPTION_ID: TEST_SUBSCRIPTION_ID })
    subscription.update_from_remote(None, mock_get_resources)

    assert subscription.as_yaml() == { azure_yaml.YAML_SUBSCRIPTION_ID: TEST_SUBSCRIPTION_ID,
             azure_yaml.YAML_RESOURCE_GROUPS:
                {
                  TEST_RESOURCE_GROUP:
                  { azure_yaml.YAML_AZURE_RESOURCE_LOCATION:
                        TEST_LOCATION_NORTH_EUROPE,
                    azure_yaml.YAML_RESOURCES:
                    { MockAzureResource.name: {} }
                  },
                  ANOTHER_RESOURCE_GROUP:
                  { azure_yaml.YAML_AZURE_RESOURCE_LOCATION:
                        TEST_LOCATION_NORTH_EUROPE,
                    azure_yaml.YAML_RESOURCES:
                    {}
                  }
                }
            }

def test_compare_subscription_with_1_remote_resource():

    resource = MockAzureResource()

    def mock_get_resources(credentials, subscription_id):
        return { TEST_RESOURCE_GROUP: { azure_yaml.YAML_AZURE_RESOURCE_LOCATION: TEST_LOCATION_NORTH_EUROPE,  azure_yaml.YAML_RESOURCES: { resource}} }

    subscription = config.AzureSubscription({ azure_yaml.YAML_SUBSCRIPTION_ID: TEST_SUBSCRIPTION_ID })
    mock_click = MockClick()

    subscription.compare_with_remote(None, mock_click, mock_get_resources)

    assert mock_click.get_content().startswith(f"Azure subscription '{TEST_SUBSCRIPTION_ID}'\nThere are differences")
