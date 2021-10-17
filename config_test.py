from azure.mgmt.resource import subscriptions
from config import Config
from ruamel.yaml import YAML
import sys

TENANT_ID="7a9376d4-7c43-480f-82ba-a090647f651d"
TENANT_NAME="MSCI v3"


def test_load_azure_tenant(cli_runner):
    config = Config.load("""
                - cloud: azure
                  name: "MSCI v3"
                  tenantId: 7a9376d4-7c43-480f-82ba-a090647f651d
                  subscriptions:
                  - name: "Global Solutions non production"
                    id: "e778a03a-847b-4d1b-9548-8f25a94d0e9f"
                """)
    tenant = config.azure
    
    assert tenant.id == TENANT_ID
    assert tenant.name == TENANT_NAME
    assert len(tenant.subscriptions) == 1
    subscription = tenant.subscriptions[0]
    assert subscription.id == "e778a03a-847b-4d1b-9548-8f25a94d0e9f"
    assert subscription.name == "Global Solutions non production"

def test_yaml_dump(cli_runner):
    with cli_runner.isolated_filesystem():
      test_file = "examle.yaml"
      with open(test_file, 'w') as f:
        f.write("""
                  - cloud: azure
                    name: "Test tenant"
                    tenantId: "7a9376d4-7c43-480f-82ba-a090647f651d"
                    subscriptions:
                    - id: "59134732-c952-4ef9-ab63-94a75300c7dc"
                      name: "Test subscription"
                  """)
      with open(test_file, "r") as f:
        config = Config.load(f)
        config.azure.subscriptions[0].add_resource({"name": "boo", "type": "baa" })
        config.save(test_file)
      with open(test_file, "r") as f:
        expected_content = """
                            - cloud: azure
                              name: "Test tenant"
                              tenantId: "7a9376d4-7c43-480f-82ba-a090647f651d"
                              subscriptions:
                              - id: "59134732-c952-4ef9-ab63-94a75300c7dc"
                                name: "Test subscription"
                                resources:
                                  - name: "boo"
                                    type: "baa"
                          """
        new_content = f.read()
        assert expected_content == new_content

