import logging
import importlib
import config

supported_cloud_providers = {}

NOT_SUPPORTED_CLOUD_PROVIDER_MESSAGE="Cloud provider {cloud_provider} is not supported"

def missing_cloud_provider_message(cloud_provider):
    return str.format("Cloud provider {cloud_provider} is not supported", cloud_provider=cloud_provider)

for cloud_provider in ["azure"]:
    try:
        cloud_provider_module = importlib.import_module("." + cloud_provider + ".core", "cloud")
        getattr(cloud_provider_module,"get_resources_from_cloud_provider")
        supported_cloud_providers[cloud_provider] = cloud_provider_module
    except (AttributeError, ModuleNotFoundError) as cloud_provider_load_error:
        logging.debug(str(cloud_provider_load_error))
        logging.warning(missing_cloud_provider_message(cloud_provider))


def assert_cloud_provider_supported(cloud_provider):
    assert cloud_provider in supported_cloud_providers, missing_cloud_provider_message(cloud_provider)

def __get_cloud_resources(cloud_resources_request):
    """ Gets all resources from cloud providers"""

    cloud_resources = []
    for cloud_request in cloud_resources_request:
        cloud_provider = get_cloud_type(cloud_request)

        if cloud_provider in supported_cloud_providers:
            cloud_resources.append(supported_cloud_providers[cloud_provider].get_resources_from_cloud_provider(cloud_request))
        else:
            logging.warning(missing_cloud_provider_message(cloud_provider))

    return cloud_resources

def print_cloud_resources(cloud, subscription_id, output):
    if cloud not in supported_cloud_providers:
        logging.warning(missing_cloud_provider_message(cloud))
        return

    config.print_cloud_resources(__get_cloud_resources( __new_azure_request([subscription_id])), output)

def __new_azure_request(subscription_ids):
    return [ { "cloud" : "azure", "subscription_ids" : subscription_ids} ]

def calculate_differences(local_config):
    logging.debug(local_config)
    for config in local_config:

        cloud = get_cloud_type(config)
        assert_cloud_provider_supported(cloud)

        for subscription in get_subscriptions(config):
            subscription_id = get_id(subscription)
            local_resources = get_resources(subscription)

            remote_configs = __get_cloud_resources( __new_azure_request([subscription_id]))

            for remote_config in remote_configs:

                for remote_subscription in get_subscriptions(remote_config):
                    remote_resources = get_resources(remote_subscription)

                return __calculate_difference_between_resources(local_resources, remote_resources)


    return []

def get_cloud_type(config):
    return require(config, "cloud", "Missing cloud attribute!")

def get_subscriptions(config):
    return require(config, "subscriptions", "Missing subscriptions!")

def get_id(subscription):
    return require(subscription, "id", "Missing 'id' for subscription!")

def get_resources(subscription):
    if "resources" in subscription:
        resources = subscription["resources"]
        assert isinstance(resources, list), "Expecting list of resources"
        return resources
    return []

def create_only_local_resource(resource):
    return [ resource, None, None ]

def create_only_remote_resource(resource):
    return [ None, None, resource ]

def create_dict_from_resources_by_name(resource_list):
    return { resource_name(resource) : resource for resource in resource_list }

def __calculate_difference_between_resources(local_resources, remote_resources):
    logging.debug(f"Local resources: {local_resources}")
    logging.debug(f"Remote resources: {remote_resources}")

    if len(local_resources) == 0 and len(remote_resources) == 0:
        return []

    if len(local_resources) == 0:
        return [ create_only_remote_resource(remote_resource) for remote_resource in remote_resources]
    elif len(remote_resources) == 0:
        return [ create_only_local_resource(local_resource) for local_resource in local_resources]
    else:
        local_resources_dict = create_dict_from_resources_by_name(local_resources)
        remote_resource_dict = create_dict_from_resources_by_name(remote_resources)

        resource_names_in_local_config_file = local_resources_dict.keys()
        resource_names_in_cloud_provider = remote_resource_dict.keys()

        resource_names_in_local_and_cloud_provider = resource_names_in_local_config_file & resource_names_in_cloud_provider

        only_local = resource_names_in_local_config_file ^ resource_names_in_local_and_cloud_provider
        only_remote = resource_names_in_cloud_provider ^ resource_names_in_local_and_cloud_provider

        diff_list = []
        for only_local_resource_name in only_local:
            diff_list.append(create_only_local_resource(local_resources_dict[only_local_resource_name]))

        for common_resource_key in resource_names_in_local_and_cloud_provider:
            resource_diffs = __compare_resource(local_resources_dict[common_resource_key], remote_resource_dict[common_resource_key])
            if resource_diffs:
                diff_list.append([ local_resources_dict[common_resource_key], resource_diffs, remote_resource_dict[common_resource_key]])

        for only_remote_resource_name in only_remote:
            diff_list.append(create_only_remote_resource(remote_resource_dict[only_remote_resource_name]))

        return diff_list


def __compare_resource(local_resource, remote_resource):
    local_keys = local_resource.keys()
    remote_keys = remote_resource.keys()

    common = local_keys & remote_keys

    only_local = local_keys ^ common
    only_remote = remote_keys ^ common

    diff = {}
    for local_resource_key in only_local:
        if local_resource[local_resource_key]:
            diff[local_resource_key] = (local_resource[local_resource_key], None)

    for common_resource_key in common:
        if local_resource[common_resource_key] and remote_resource[common_resource_key]:
            if local_resource[common_resource_key] != remote_resource[common_resource_key]:
                diff[common_resource_key] = (local_resource[common_resource_key], remote_resource[common_resource_key])

    for remote_resource_key in only_remote:
        if remote_resource[remote_resource_key]:
            diff[remote_resource_key] = (None, remote_resource[remote_resource_key])

    return diff

def resource_name(resource):
    return resource["name"]

def require(dict_object, key, error_message):
    if key not in dict_object:
        raise ValueError(error_message)
    else:
        return dict_object[key]
