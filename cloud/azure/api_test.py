import logging
import pytest
import api

logging.basicConfig(level=logging.DEBUG)

TEST_SUBSCRIPTION_ID="5ed44b1f-1379-4af2-b7c5-097bbd2e2ee2"
TEST_RESOURCE_GROUP = "test_resource_group"

@pytest.fixture
def login():
    return api.login()

@pytest.fixture
def resource_group(login):
    api.delete_resource_group(login, TEST_SUBSCRIPTION_ID, TEST_RESOURCE_GROUP)
    api.update_resource_group(login, TEST_SUBSCRIPTION_ID, TEST_RESOURCE_GROUP, resource_group={
            api.YAML_AZURE_RESOURCE_LOCATION: "northeurope"
        })
    yield TEST_RESOURCE_GROUP
    api.delete_resource_group(login, TEST_SUBSCRIPTION_ID, TEST_RESOURCE_GROUP)


def test_resource_group_api(login, resource_group, cli_runner):
    assert api.check_existence(login, TEST_SUBSCRIPTION_ID, resource_group), f"{resource_group} shoud exist"
