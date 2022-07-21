# What is this?

I am playing with an idea of a command-line tool which would help managing cloud infrastructure better than Terraform does.
Terraform is more complicated than necessary.

# How does it work?
You download and you can start importing, modifyig cloud infrastructure code.

# Status
Not that useful yet.


# Examples

## Dumping Azure config to stdout
```
python iac.py describe -t azure -s "5ed44b1f-1379-4af2-b7c5-097bbd2e2ee2"
- cloud: azure
  subscriptions:
  - id: 5ed44b1f-1379-4af2-b7c5-097bbd2e2ee2
    resourceGroups:
      NetworkWatcherRG:
        resources:
        - name: NetworkWatcher_centralus
          type: Microsoft.Network/networkWatchers
          location: centralus
        - name: NetworkWatcher_northeurope
          type: Microsoft.Network/networkWatchers
          location: northeurope
      azure_devops_resources:
        resources: []
```

** iac.oy
*** status
    local_config = config.load_yaml from file
    local_config.compare_with_remote

*** pull
    local_config = config.load_yaml from file
    local_config.update_from_remote(credential) 
    config.save_yaml(local.as_yaml(), file)