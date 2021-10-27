from config import load_yaml, save_yaml
import io
import pytest

TENANT_ID="7a9376d4-7c43-480f-82ba-a090647f651d"
SUBSCRIPTION_ID="59134732-c952-4ef9-ab63-94a75300c7dc"
SUBSCRIPTION_NAME="GlobalSolutions_Sandbox"

TEST_YAML=f"""\
- cloud: azure
  tenantId: {TENANT_ID}
  subscriptions:
  - id: {SUBSCRIPTION_ID}
    name: {SUBSCRIPTION_NAME}
"""

def test_not_supported_provider(cli_runner):
    with pytest.raises(ValueError):
        load_yaml(f"""\
- cloud: unknown_cloud
""")

def test_load_azure_tenant(cli_runner):
    config = load_yaml(TEST_YAML)
    tenant = config.azure
    
    assert tenant.id == TENANT_ID
    assert len(tenant.subscriptions) == 1
    subscription = tenant.subscriptions[0]
    assert subscription.id == SUBSCRIPTION_ID
    assert subscription.name == SUBSCRIPTION_NAME

def test_save_azure_resources(cli_runner):
    config = load_yaml(TEST_YAML)
    config.azure.subscriptions[0].add_resource({"name": "boo", "type": "baa" })
    with io.StringIO() as test_output:
      save_yaml(config.yaml_config, test_output)
      expected_content = f"""\
- cloud: azure
  tenantId: {TENANT_ID}
  subscriptions:
  - id: {SUBSCRIPTION_ID}
    name: {SUBSCRIPTION_NAME}
    resources:
    - name: boo
      type: baa
"""
      assert expected_content == test_output.getvalue()

