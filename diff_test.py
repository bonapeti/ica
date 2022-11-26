import core


def test_remote_diff():
    remote_resource = { "name": "remote_resource"}
    remote_difference = core.RemoteOnlyResourceDifference(remote_resource)

    local_resources = []
    remote_difference.patch_local_config(local_resources)
    assert remote_resource == local_resources[0]
