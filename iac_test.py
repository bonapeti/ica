from iac import main, default_filename
from config import AZURE
from config_test import TEST_YAML, TEST_SUBSCRIPTION_ID

TEST_SUBSCRIPTION_ID="5ed44b1f-1379-4af2-b7c5-097bbd2e2ee2"

def prepare_test_config_file():
    with open(default_filename, 'w') as f:
          f.write(TEST_YAML)

def test_diff_without_file(cli_runner):
    result = cli_runner.invoke(main, ["diff"])
    assert result.output == f"Cannot find {default_filename}\n"
    assert result.exit_code == 0

def test_diff_with_file(cli_runner):

    with cli_runner.isolated_filesystem():
      prepare_test_config_file()
      result = cli_runner.invoke(main, ["diff"])
      assert result.output.startswith(f"Azure subscription '{TEST_SUBSCRIPTION_ID}'\nNo changes")
      assert result.exit_code == 0

def test_show(cli_runner):
    
    result = cli_runner.invoke(main, ["show","-t",AZURE,"-s",TEST_SUBSCRIPTION_ID])
    with open("./test_subscription.yaml","r") as expected_file:
      assert result.output == expected_file.read()
    assert result.exit_code == 0


def test_pull_with_file(cli_runner):

    with cli_runner.isolated_filesystem():
      prepare_test_config_file()
      result = cli_runner.invoke(main, ["pull"])
      assert result.output == ""
      assert result.exit_code == 0
      
      
