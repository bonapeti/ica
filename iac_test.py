from iac import main, open_file_for_read, open_file_for_write, DEFAULT_FILENAME
import azure_yaml
import azure_api
from config_test import TEST_YAML, TEST_SUBSCRIPTION_ID, TEST_LOCATION_NORTH_EUROPE

TEST_SUBSCRIPTION_ID="5ed44b1f-1379-4af2-b7c5-097bbd2e2ee2"

def prepare_test_config_file():
    """Prepares a test configuration file infrastructure.yaml with default content"""
    prepare_test_config_file_with_content(TEST_YAML)

def prepare_test_config_file_with_content(content):
    """Prepares a test configuration file infrastructure.yaml with specific content"""
    with open_file_for_write(DEFAULT_FILENAME) as test_config_file:
        test_config_file.write(content)

def test_diff_without_file(cli_runner):
    result = cli_runner.invoke(main, ["diff"])
    assert result.output == f"Cannot find {DEFAULT_FILENAME}\n"
    assert result.exit_code == 0

mock_crednetial = {}

def mocklogin():
    print("mocklogin")
    return mock_crednetial

def test_diff_with_file(cli_runner, monkeypatch):

    remote_resources = {
        "NetworkWatcherRG" :
            {
                azure_yaml.YAML_AZURE_RESOURCE_LOCATION : TEST_LOCATION_NORTH_EUROPE,
                azure_yaml.YAML_RESOURCES : {}
            }
    }

    def mockget_resources():
        print("mockget_resources")
        return remote_resources


    with monkeypatch.context() as m:
        m.setattr(azure_api, "login", mocklogin)
        m.setattr(azure_api, "get_resources", mockget_resources)
        with cli_runner.isolated_filesystem():
            prepare_test_config_file()
            result = cli_runner.invoke(main, ["diff"])
            assert result.output == f"Azure subscription '{TEST_SUBSCRIPTION_ID}'\nNo changes"
            assert result.exit_code == 0

def test_show(cli_runner):
    result = cli_runner.invoke(main, ["show","-c",azure_yaml.AZURE,"-s",TEST_SUBSCRIPTION_ID])
    with open_file_for_read("./test_subscription.yaml") as expected_file:
        assert result.output == expected_file.read()
    assert result.exit_code == 0


def test_pull_with_file(cli_runner):
    with cli_runner.isolated_filesystem():
        prepare_test_config_file()
        result = cli_runner.invoke(main, ["pull"])
        assert result.output == ""
        assert result.exit_code == 0

def test_push(cli_runner):
    new_resource_group_name = "NewResourceGroup"
    with cli_runner.isolated_filesystem():
        prepare_test_config_file_with_content(f"""\
- cloud: azure
  subscriptions:
  - id: {TEST_SUBSCRIPTION_ID}
    resourceGroups:
      {new_resource_group_name}:
        location: northeurope
""")
        result = cli_runner.invoke(main, ["push"])
        assert result.output == ""
        assert result.exit_code == 0
        with azure_api.login() as credential:
            resource_dict = azure_api.get_resources(credential, TEST_SUBSCRIPTION_ID)
            assert resource_dict[new_resource_group_name], "Azure subscription should have new resource group"
