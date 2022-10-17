
yaml_attributes = ("name", "type", "location")

def as_yaml(azure_resource_group):
    yaml = {}
    for yaml_attribute in yaml_attributes:
        yaml[yaml_attribute] = getattr(azure_resource_group, yaml_attribute)
    if azure_resource_group.tags:
        yaml["tags"] = azure_resource_group.tags
    return yaml
