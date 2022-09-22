from cc import main, DEFAULT_FILENAME
import core
import config
import cloud.azure.api

TEST_SUBSCRIPTION_ID="5ed44b1f-1379-4af2-b7c5-097bbd2e2ee2"
TEST_YAML=f"""\
- cloud: azure
  subscriptions:
  - id: {TEST_SUBSCRIPTION_ID}
    resources: []
"""

def prepare_test_config_file():
    """Prepares a test configuration file infrastructure.yaml with default content"""
    prepare_test_config_file_with_content(TEST_YAML)

def prepare_test_config_file_with_content(content):
    """Prepares a test configuration file infrastructure.yaml with specific content"""
    with config.open_file_for_write(DEFAULT_FILENAME) as test_config_file:
        test_config_file.write(content)

def test_show(cli_runner, monkeypatch):

    def azure_get_all_resources(credentials, subscription_id):
        return []

    monkeypatch.setattr(cloud.azure.api, "get_all_resources", azure_get_all_resources)

    result = cli_runner.invoke(main, ["show","-c","azure","-s",TEST_SUBSCRIPTION_ID])
    assert result.exit_code == 0
    assert result.output == f"""\
- cloud: azure
  subscriptions:
  - id: {TEST_SUBSCRIPTION_ID}
    resources: []
"""

def test_no_diff(cli_runner, monkeypatch):

    def azure_get_all_resources(credentials, subscription_id):
        return []

    monkeypatch.setattr(cloud.azure.api, "get_all_resources", azure_get_all_resources)

    with cli_runner.isolated_filesystem():
        prepare_test_config_file()
        result = cli_runner.invoke(main, ["diff"])
        assert result.output == f"Azure subscription '{TEST_SUBSCRIPTION_ID}'\nNo changes\n"
        assert result.exit_code == 0

def test_diff_local_resource_added(cli_runner, monkeypatch):

    def azure_get_all_resources(credentials, subscription_id):
        return [ "local_resource_group"]

    monkeypatch.setattr(cloud.azure.api, "get_all_resources", azure_get_all_resources)

    with cli_runner.isolated_filesystem():
        prepare_test_config_file()
        result = cli_runner.invoke(main, ["diff"])
        assert result.output == "Azure subscription '" + TEST_SUBSCRIPTION_ID + "'\nThere are differences:\n"
        assert result.exit_code == 0
