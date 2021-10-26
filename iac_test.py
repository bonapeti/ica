from iac import main, default_filename
from config_test import TEST_YAML, SUBSCRIPTION_ID, SUBSCRIPTION_NAME

TEST_SUBSCRIPTION_ID="59134732-c952-4ef9-ab63-94a75300c7dc"
AZURE = "azure"

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
      assert result.output == f"Azure subscription '{SUBSCRIPTION_NAME}'\n\tThere are differences\n"
      assert result.exit_code == 0

def test_describe(cli_runner):
    
    result = cli_runner.invoke(main, ["describe","-t",AZURE,"-s",TEST_SUBSCRIPTION_ID])
    with open("./test_gs_sandbox.yaml","r") as expected_file:
      assert result.output == expected_file.read()
    assert result.exit_code == 0


def test_diff_with_file(cli_runner):

    with cli_runner.isolated_filesystem():
      prepare_test_config_file()
      result = cli_runner.invoke(main, ["pull"])
      assert result.output == ""
      assert result.exit_code == 0
      
      
