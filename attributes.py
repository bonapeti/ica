def object_as_yaml(object, object_description):
  assert isinstance(object_description, dict), "Expecting dict as object description"

  yaml = {}
  for attribute_name, attribute_description in object_description.items():
    value = getattr(object, attribute_name)
    if value and not is_ignorable(attribute_description):
      yaml[attribute_name] = value

  return yaml



def is_ignorable(description):
  return description.get("ignore_if_empty", False)
