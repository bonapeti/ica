from azure.mgmt.resource import subscriptions
from config import Config
from ruamel.yaml import YAML
import sys
import io

TENANT_ID="7a9376d4-7c43-480f-82ba-a090647f651d"
TENANT_NAME="MSCI v3"
SUBSCRIPTION_ID="e778a03a-847b-4d1b-9548-8f25a94d0e9f"
SUBSCRIPTION_NAME="Global Solutions non production"

TEST_YAML=f"""\
- cloud: azure
  name: {TENANT_NAME}
  tenantId: {TENANT_ID}
  subscriptions:
  - id: {SUBSCRIPTION_ID}
    name: {SUBSCRIPTION_NAME}
"""

def test_load_azure_tenant(cli_runner):
    config = Config.load(TEST_YAML)
    tenant = config.azure
    
    assert tenant.id == TENANT_ID
    assert tenant.name == TENANT_NAME
    assert len(tenant.subscriptions) == 1
    subscription = tenant.subscriptions[0]
    assert subscription.id == SUBSCRIPTION_ID
    assert subscription.name == SUBSCRIPTION_NAME

def test_save_azure_resources(cli_runner):
    config = Config.load(TEST_YAML)
    config.azure.subscriptions[0].add_resource({"name": "boo", "type": "baa" })
    with io.StringIO() as test_output:
      config.save(test_output)
      expected_content = f"""\
- cloud: azure
  name: {TENANT_NAME}
  tenantId: {TENANT_ID}
  subscriptions:
  - id: {SUBSCRIPTION_ID}
    name: {SUBSCRIPTION_NAME}
    resources:
    - name: boo
      type: baa
"""
      assert expected_content == test_output.getvalue()

