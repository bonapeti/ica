from ica import main, default_filename


def test_pull_without_file(cli_runner):
    result = cli_runner.invoke(main, ["pull"])
    assert result.exit_code == 0
    assert result.output == f"Cannot find {default_filename}\n"

def test_pull_with_file(cli_runner):

    with cli_runner.isolated_filesystem():
      with open(default_filename, 'w') as f:
          f.write("""
                  - name: "My infrastructure"
                    type: azure
                    tenant: "900a843e-af52-4bc8-9009-4676366d9d97"
                    subscription:
                      id: "5ed44b1f-1379-4af2-b7c5-097bbd2e2ee2"
                  """)
      result = cli_runner.invoke(main, ["pull"])
      assert result.exit_code == 0
      assert result.output == f"Loaded file\n"
