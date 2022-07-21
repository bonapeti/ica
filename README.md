# What is this?

I am playing with an idea of a command-line tool which would help managing cloud infrastructure better than Terraform does.

# How does it work?
You download and you can start importing, modifyig cloud infrastructure code.

# Status
Not that useful yet.


# Examples

## Dumps current status from actual infrastructure to stdout
```
λ python iac.py describe -t azure -s "5ed44b1f-1379-4af2-b7c5-097bbd2e2ee2"
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

## Compares current status from actual infrastructure and the description in file
```
λ python iac.py status -f test_subscription.yaml
Azure subscription '5ed44b1f-1379-4af2-b7c5-097bbd2e2ee2'
        There are differences. Local: 2, remote: 2
```

## Pulls current status from actual infrastructure and updates file
```
λ python iac.py pull -f test_subscription.yaml
```

