import azure_api

def get_cloud_resources(cloud_resources_request):
    """ Gets all resources from cloud providers"""

    cloud_resources = []
    for cloud in cloud_resources_request:
        cloud_resource = { "cloud": "azure"}
        cloud_resources.append(cloud_resource)

        if azure_api.SUBSCRIPTION_IDS in cloud:
            subscription_ids = cloud[azure_api.SUBSCRIPTION_IDS]
            if len(subscription_ids) > 0:


                with azure_api.login() as credential:
                    subscriptions = []
                    cloud_resource["subscriptions"] = subscriptions

                    for subscription_id in subscription_ids:
                        subscriptions.append({ "id": subscription_id,
                                 "resources": azure_api.get_all_resources(credential, subscription_id)})
    return cloud_resources
