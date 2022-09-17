import cloud.azure.api

def get_cloud_resources(cloud_resources_request):
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
