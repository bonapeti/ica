import cloud.azure.api
import config

def __get_cloud_resources(cloud_resources_request):
    """ Gets all resources from cloud providers"""

    cloud_resources = []
    for cloud_request in cloud_resources_request:
        cloud_resource = { "cloud": "azure"}
        cloud_resources.append(cloud_resource)

        if cloud.azure.api.SUBSCRIPTION_IDS in cloud_request:
            subscription_ids = cloud_request[cloud.azure.api.SUBSCRIPTION_IDS]
            if len(subscription_ids) > 0:


                with cloud.azure.api.login() as credential:
                    subscriptions = []
                    cloud_resource["subscriptions"] = subscriptions

                    for subscription_id in subscription_ids:
                        subscriptions.append({ "id": subscription_id,
                                 "resources": cloud.azure.api.get_all_resources(credential, subscription_id)})
    return cloud_resources

def print_cloud_resources(cloud, subscription_id, output):
    config.print_cloud_resources(__get_cloud_resources( [ { "type" : cloud, "subscription_ids" : [subscription_id]} ]), output)

def calculate_differences(local_config):
    differences = []
    for config in local_config:
        cloud = require(config, "cloud", "Missing cloud attribute!")
        assert "azure" == cloud
        subscriptions = require(config, "subscriptions", "Missing subscriptions!")
        for subscription in subscriptions:
            subscription_id = require(subscription, "id", "Missing 'id' for subscription!")
            local_resources = []
            if "resources" in subscription:
                local_resources = subscription["resources"]

            remote_configs = __get_cloud_resources( [ { "type" : cloud, "subscription_ids" : [subscription_id]} ])

            for remote_config in remote_configs:
                remote_cloud = require(remote_config, "cloud", "Missing cloud attribute!")
                assert "azure" == remote_cloud
                remote_subscriptions = require(remote_config, "subscriptions", "Missing subscriptions!")
                for remote_subscriptions in remote_subscriptions:
                    remote_subscription_id = require(remote_subscriptions, "id", "Missing 'id' for subscription!")
                    remote_resources = []
                    if "resources" in remote_subscriptions:
                        remote_resources = remote_subscriptions["resources"]

                if len(local_resources) == 0 and len(remote_resources) == 0:
                    return []
                else:
                    if len(local_resources) == 0:
                        return remote_resources


    return differences

def require(dict_object, key, error_message):
    if key not in dict_object:
        raise ValueError(error_message)
    else:
        return dict_object[key]
