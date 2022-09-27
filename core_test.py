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

def test_basic_difference_calculation():
    assert [] == core.__calculate_difference_between_resources([],[])

    remote_resource = { "name":"remote_resource"}
    assert [ ["","", remote_resource]] == core.__calculate_difference_between_resources([],[remote_resource])

    local_resource = { "name":"local_resource" }
    assert  [[local_resource,"", ""]] == core.__calculate_difference_between_resources([local_resource],[])
