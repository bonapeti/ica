def as_yaml(azure_resource_group):
    return { "id": azure_resource_group.id,
                        "name": azure_resource_group.name,
                        "type": azure_resource_group.type,
                        "location": azure_resource_group.location,
                        "tags": azure_resource_group.tags,
                        "managed_by": azure_resource_group.managed_by,
                        "properties":convert_azure_resource_group_properties(azure_resource_group.properties)
                        }

def convert_azure_resource_group_properties(azure_resource_group_properties):
    return { "provisioning_state": azure_resource_group_properties.provisioning_state}
