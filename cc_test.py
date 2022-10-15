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

def mock_azure_resources(monkeypatch, resources):
    def azure_get_all_resources(credentials, subscription_id):
        return resources
    monkeypatch.setattr(cloud.azure.api, "get_all_resources", azure_get_all_resources)

def assert_normal_output(result, expected_output):
    assert result.exit_code == 0
    assert result.output == expected_output

def test_show(cli_runner, monkeypatch):

    mock_azure_resources(monkeypatch, [])

    result = cli_runner.invoke(main, ["show","-c","azure","-s",TEST_SUBSCRIPTION_ID])

    assert_normal_output(result, f"""\
- cloud: azure
  subscriptions:
  - id: {TEST_SUBSCRIPTION_ID}
    resources: []
""")

def test_no_diff(cli_runner, monkeypatch):

    mock_azure_resources(monkeypatch, [])

    with cli_runner.isolated_filesystem():
        prepare_test_config_file()
        result = cli_runner.invoke(main, ["diff"])
        assert_normal_output(result, "No changes\n")


def test_diff_local_resource_added(cli_runner, monkeypatch):

    mock_azure_resources(monkeypatch, [ "local_resource_group"])

    with cli_runner.isolated_filesystem():
        prepare_test_config_file()
        result = cli_runner.invoke(main, ["diff"])
        assert_differences(result)

def test_diff_remote_resource_added(cli_runner, monkeypatch):

    mock_azure_resources(monkeypatch, [])

    with cli_runner.isolated_filesystem():
        prepare_test_config_file_with_content(f"""\
- cloud: azure
  subscriptions:
  - id: {TEST_SUBSCRIPTION_ID}
    resources:
    - name: remote_resource
""")
        result = cli_runner.invoke(main, ["diff"])
        assert_differences(result)

def assert_differences(result):
    assert result.output.startswith("There are differences\n")
    assert result.exit_code == 0
