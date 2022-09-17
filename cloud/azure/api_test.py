import logging
import pytest
import api
import azure_yaml
import config_test

logging.basicConfig(level=logging.DEBUG)

@pytest.fixture
def login():
    return api.login()

@pytest.fixture
def resource_group(login):
    api.delete_resource_group(login, config_test.TEST_SUBSCRIPTION_ID, config_test.TEST_RESOURCE_GROUP)
    api.update_resource_group(login, config_test.TEST_SUBSCRIPTION_ID, config_test.TEST_RESOURCE_GROUP, resource_group={
            azure_yaml.YAML_AZURE_RESOURCE_LOCATION: "northeurope"
        })
    yield config_test.TEST_RESOURCE_GROUP
    api.delete_resource_group(login, config_test.TEST_SUBSCRIPTION_ID, config_test.TEST_RESOURCE_GROUP)


def test_resource_group_api(login, resource_group, cli_runner):
    assert api.check_existence(login, config_test.TEST_SUBSCRIPTION_ID, resource_group), f"{resource_group} shoud exist"
