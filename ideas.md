# Desribe
## Loads configuration from Azure and prints content to stdout
### Arguments: subscription_id

- subscription_details = azure.get_subscription(subscription_id)
- azure_resources = azure.get_resources(subscription_id)
- yaml = convert_to_yaml(azure_resources)
- save(yaml, stdout)

# Pull
## Loads local configuration file, downloads latest from Azure and updates configuration file in place
### Arguments: filename
- yaml = load_config_file(filename)
- subscription_id = get_subscription_id(yaml)
- local_resources = get_local_resources(yaml)
- azure_resources = azure.get_resources(subscription_id)
- updates_local(local_resources, azure_resources)
- new_yaml = convert_to_yaml(updates_local)
- update_yaml(yaml, new_yaml)
- save(yaml, file)

# Status
## Loads local configuration file, downloads latest from Azure. Compares local config with Azure and displays differences
### Arguments: filename
- yaml = load_config_file(filename)
- subscription_id = get_subscription_id(yaml)
- local_resources = get_local_resources(yaml)
- azure_resources = azure.get_resources(subscription_id)
- diff = compare(local_resources, azure_resources)
- print(diff, stdout)

# Push
## Loads local configuration file, downloads latest from Azure. Pushes difference to Azure
### Arguments: filename
- yaml = load_config_file(filename)
- subscription_id = get_subscription_id(yaml)
- local_resources = get_local_resources(yaml)
- azure_resources = azure.get_resources(subscription_id)
- diff = compare(local_resources, azure_resources)
- result = azure.update(diff)
- print(result, stdout)