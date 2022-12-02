import core
import cloud.azure.api
from contextlib import contextmanager

MOCK_CREDENTIAL_ID="azure_credential"

@contextmanager
def mock_azure_login():
    yield MOCK_CREDENTIAL_ID

def local_config_without_resources():
    return local_config("test_subscription_id",[])

def local_config(subscription_id, resources):
    return [{
                                "cloud": "azure",
                                "subscriptions": [
                                        {
                                            "id": subscription_id,
                                            "resources": resources
                                        }
                                    ]
                        }]

def test_get_resources(monkeypatch):

    login_id = "login_id"
    test_subscription_id = "subscription_id"
    expected_resources = [{
                                "cloud": "azure",
                                "subscriptions": [
                                        {
                                            "id": test_subscription_id,
                                            "resources": []
                                        }
                                    ]
                        }]


    def get_all_resources(credentials, subscription_id):
        assert subscription_id == test_subscription_id
        return []

    monkeypatch.setattr(cloud.azure.api, "login", mock_azure_login)
    monkeypatch.setattr(cloud.azure.api, "get_all_resources", get_all_resources)

    assert expected_resources == core.__get_cloud_resources([ { "cloud": "azure", cloud.azure.api.SUBSCRIPTION_IDS: [ test_subscription_id]}])

def assert_no_difference(local_resources, remote_resources):
    assert [] == core.__calculate_difference_between_resources(local_resources,remote_resources)

def test_basic_difference_calculation():
    assert_no_difference([],[])

    remote_resource = { "name":"remote_resource"}
    assert [ core.create_only_remote_resource(remote_resource) ] == core.__calculate_difference_between_resources([],[remote_resource])

    local_resource = { "name":"local_resource" }
    assert [ core.create_only_local_resource(local_resource) ] == core.__calculate_difference_between_resources([local_resource],[])

def test_calculate_difference_same_resource_in_local_and_remote_should_result_no_difference():

    local_resource = { "name":"resource" }
    remote_resource = { "name":"resource"}
    assert_no_difference([local_resource],[remote_resource])

def test_calculate_difference_different_resources_in_local_and_remote_should_result_shows_difference():

    local_resource = { "name":"resource1" }
    remote_resource = { "name":"resource2"}
    assert [ core.create_only_local_resource(local_resource), core.create_only_remote_resource(remote_resource)] == core.__calculate_difference_between_resources([local_resource],[remote_resource])

def test_calculate_difference_same_resource_with_different_values_should_result_shows_difference():

    local_resource = { "name":"resource", "value": "value1" }
    remote_resource = { "name":"resource", "value": "value2"}
    assert [ core.ResourceAttributeDifferences("resource", { "value": ("value1","value2")})] == core.__calculate_difference_between_resources([local_resource],[remote_resource])

def test_calculate_difference_same_resource_with_tags_in_remote():

    local_resource = { "name":"resource" }
    remote_resource = { "name":"resource", "tags": { "name" : "value"}}
    assert [ core.ResourceAttributeDifferences("resource", { "tags": (None,{ "name" : "value"})})] == core.__calculate_difference_between_resources([local_resource],[remote_resource])

def test_calculate_difference_1_local_2_remote():

    local_resource = { "name":"resource" }
    remote_resource1 = { "name":"resource"}
    remote_resource2 = { "name":"resource2"}
    assert [ core.create_only_remote_resource(remote_resource2) ] == core.__calculate_difference_between_resources([local_resource],[remote_resource1, remote_resource2])

def test_calculate_difference_2_local_1_remote():

    local_resource = { "name":"resource" }
    local_resource2 = { "name":"resource2" }
    remote_resource = { "name":"resource"}
    assert [core.create_only_local_resource(local_resource2) ] == core.__calculate_difference_between_resources([local_resource, local_resource2],[remote_resource])

def test_apply_empty_remote_changes(monkeypatch):
    def calculate_differences(local_config):
        return []

    monkeypatch.setattr(core, "calculate_differences", calculate_differences)
    assert not core.apply_remote_changes([])

def mock_differences(monkeypatch, differences):
    def calculate_differences(local_config):
        return differences

    monkeypatch.setattr(core, "calculate_differences", calculate_differences)

def test_apply_remote_changes_with_only_local_changes(monkeypatch):

    mock_differences(monkeypatch, [ core.create_only_local_resource({ "name" : "local_resource"})])
    assert not core.apply_remote_changes(local_config_without_resources())

def test_apply_remote_changes_with_only_local_changes(monkeypatch):

    mock_differences(monkeypatch, [ core.create_only_remote_resource({ "name" : "remote_resource"})])

    new_config = core.apply_remote_changes(local_config_without_resources())
    assert new_config

class MockResourceGroupUpdate:

    expected_subscription_id = None
    expected_resource_group_name = None
    expected_resource_group = None

    actual_credentials = None
    actual_subscription_id = None
    actual_resource_group_name = None
    actual_resource_group = None

    def __init__(self, expected_subscription_id, expected_resource_group_name, expected_resource_group ):
        self.expected_subscription_id = expected_subscription_id
        self.expected_resource_group_name = expected_resource_group_name
        self.expected_resource_group = expected_resource_group

    def verify(self):
        assert MOCK_CREDENTIAL_ID == self.actual_credentials
        assert self.expected_subscription_id == self.actual_subscription_id
        assert self.expected_resource_group_name == self.actual_resource_group_name
        assert self.expected_resource_group == self.actual_resource_group



def test_apply_remote_changes_with_only_local_changes(monkeypatch):

    subscription = "test_subscription"
    new_resource = { "name" : "local_resource"}

    expected_resource_group_update = MockResourceGroupUpdate(subscription, "local_resource", new_resource)

    def update_resource_group(credentials, subscription_id, resource_group_name: str, resource_group: dict):
        expected_resource_group_update.actual_credentials = credentials
        expected_resource_group_update.actual_subscription_id = subscription_id
        expected_resource_group_update.actual_resource_group_name = resource_group_name
        expected_resource_group_update.actual_resource_group = resource_group


    monkeypatch.setattr(cloud.azure.api, "login", mock_azure_login)
    monkeypatch.setattr(cloud.azure.api, "update_resource_group", update_resource_group)

    mock_differences(monkeypatch, [ core.create_only_local_resource(new_resource)])
    assert core.apply_local_changes(local_config(subscription, [new_resource]))
    expected_resource_group_update.verify()
