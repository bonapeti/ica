from cc import main
import core
import config

TEST_SUBSCRIPTION_ID="5ed44b1f-1379-4af2-b7c5-097bbd2e2ee2"

def test_show(cli_runner, monkeypatch):

    test_output = "test_output"
    test_resources = {}

    def get_cloud_resources(cloud_resources_request):
        return test_resources

    def print_cloud_resources(cloud_resources, output):
        assert test_resources == cloud_resources
        output.write(test_output)

    monkeypatch.setattr(core, "get_cloud_resources", get_cloud_resources)
    monkeypatch.setattr(config, "print_cloud_resources", print_cloud_resources)

    result = cli_runner.invoke(main, ["show","-c","azure","-s",TEST_SUBSCRIPTION_ID])
    assert result.exit_code == 0
    assert result.output == test_output
