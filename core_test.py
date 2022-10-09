import core
import cloud.azure.api

class MockAzureCredential:
    def __init__(self):
        pass

    def __enter__(self):
        return "login"

    def __exit__(self, a, b, c):
        pass



def test_get_resources(monkeypatch):

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

    def azure_login():
        return MockAzureCredential()

    monkeypatch.setattr(cloud.azure.api, "login", azure_login)
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
    assert [ [ local_resource, { "value": ("value1","value2")}, remote_resource]] == core.__calculate_difference_between_resources([local_resource],[remote_resource])


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
