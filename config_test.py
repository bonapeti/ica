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
