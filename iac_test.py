from iac import main, default_filename


def test_pull_without_file(cli_runner):
    result = cli_runner.invoke(main, ["status"])
    assert result.exit_code == 0
    assert result.output == f"Cannot find {default_filename}\n"

def test_status_with_file(cli_runner):

    with cli_runner.isolated_filesystem():
      with open(default_filename, 'w') as f:
          f.write("""
                  - cloud: azure
                    name: "Test tenant"
                    tenantId: "7a9376d4-7c43-480f-82ba-a090647f651d"
                    subscriptions:
                    - id: "59134732-c952-4ef9-ab63-94a75300c7dc"
                      name: "Test subscription"
                  """)
      result = cli_runner.invoke(main, ["status"])
      assert result.exit_code == 0
      assert result.output == f"Subscription 'Test subscription': local resources: 0, remote resources: 18\n"
      
      
