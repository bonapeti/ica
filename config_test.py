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
