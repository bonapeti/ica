import cloud.azure.api

def get_resources_from_cloud_provider(cloud_request):
    cloud_resource = { "cloud": "azure"}

    if cloud.azure.api.SUBSCRIPTION_IDS in cloud_request:
        subscription_ids = cloud_request[cloud.azure.api.SUBSCRIPTION_IDS]
        if len(subscription_ids) > 0:


            with cloud.azure.api.login() as credential:
                subscriptions = []
                cloud_resource["subscriptions"] = subscriptions

                for subscription_id in subscription_ids:
                    subscriptions.append({ "id": subscription_id,
                                "resources": cloud.azure.api.get_all_resources(credential, subscription_id)})

    return cloud_resource

def create_new_resource(subscription_id, new_resoure):
    with cloud.azure.api.login() as credential:
        cloud.azure.api.update_resource_group(credential, subscription_id, new_resoure["name"], new_resoure)

def update_resource(subscription_id, resource):
    with cloud.azure.api.login() as credential:
        cloud.azure.api.update_resource_group(credential, subscription_id, resource["name"], resource)

def delete_resource(subscription_id, resource):
    with cloud.azure.api.login() as credential:
        cloud.azure.api.delete_resource_group(credential, subscription_id, resource["name"])
