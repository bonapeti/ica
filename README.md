# What is this?

I am playing with an idea of a command-line tool which would help managing cloud infrastructure better than Terraform does.
Terraform is more complicated than necessary.

# How does it work?
You download and you can start importing, modifyig cloud infrastructure code.

# Status
Just playing with the code, far from being anything useful.

# Examples


** iac.oy
*** status
    local_config = config.load_yaml from file
    local_config.compare_with_remote
*** describe
    local_config = new_azure_config(subscription_id)
    local_config.update_from_remote(credential)    
    config.save_yaml(local_config.as_yaml(), sys.stdout)
*** pull
    local_config = config.load_yaml from file
    local_config.update_from_remote(credential) 
    config.save_yaml(local.as_yaml(), file)