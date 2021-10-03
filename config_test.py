from config import Config

TENANT_ID="7a9376d4-7c43-480f-82ba-a090647f651d"
TENANT_NAME="MSCI v3"


def test_load_azure_tenant(cli_runner):
    config = Config.load("""
                - cloud: azure
                  name: "MSCI v3"
                  tenantId: 7a9376d4-7c43-480f-82ba-a090647f651d
                  subscruptions:
                  - name: "Global Solutions non production"
                    id: "e778a03a-847b-4d1b-9548-8f25a94d0e9f"
                """)
    tenant = config.azure
    
    assert tenant.id == TENANT_ID
    assert tenant.name == TENANT_NAME


