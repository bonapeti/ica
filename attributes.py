def object_as_yaml(object, object_description):
  assert isinstance(object_description, dict), "Expecting dict as object description"

  yaml = {}
  for attribute_name, attribute_description in object_description.items():
    value = getattr(object, attribute_name)
    if value:
      yaml[attribute_name] = value

  return yaml
