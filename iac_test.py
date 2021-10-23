from iac import main, default_filename
from config_test import TEST_YAML, SUBSCRIPTION_ID, SUBSCRIPTION_NAME

def prepare_test_config_file():
    with open(default_filename, 'w') as f:
          f.write(TEST_YAML)

def test_status_without_file(cli_runner):
    result = cli_runner.invoke(main, ["status"])
    assert result.output == f"Cannot find {default_filename}\n"
    assert result.exit_code == 0

def test_status_with_file(cli_runner):

    with cli_runner.isolated_filesystem():
      prepare_test_config_file()
      result = cli_runner.invoke(main, ["status"])
      assert result.output == f"Subscription '{SUBSCRIPTION_NAME}': local resources: 0, remote resources: 337\n"
      assert result.exit_code == 0

def test_show(cli_runner):

    result = cli_runner.invoke(main, ["describe","-s","59134732-c952-4ef9-ab63-94a75300c7dc"])
    with open("./test_gs_sandbox.yaml","r") as expected_file:
      assert result.output == expected_file.read()
    assert result.exit_code == 0


def test_diff_with_file(cli_runner):

    with cli_runner.isolated_filesystem():
      prepare_test_config_file()
      result = cli_runner.invoke(main, ["pull"])
      assert result.output == ""
      assert result.exit_code == 0
      
      
