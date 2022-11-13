import logging
from ruamel.yaml import YAML
import cloud.azure.api
from tabulate import tabulate
import azure_yaml

SUPPORTED_PROVIDERS=[azure_yaml.AZURE]

def print_cloud_resources(cloud_resources, output) -> None:
    ruamel_yaml = YAML()
    ruamel_yaml.dump(cloud_resources, output)

def open_file_for_read(file):
    """Opens file for reading with utf-8 encoding"""
    logging.debug(f"Opening file '{file}'")
    return open(file,"r", encoding="utf-8")

def open_file_for_write(file):
    """Opens file for writing with utf-8 encoding"""
    return open(file,"w", encoding="utf-8")

def expect_string(dict_var, name, error_message):
    value = dict_var.get(name)
    if value is None:
        raise ValueError(error_message)
    assert isinstance(value, str)
    return value

def load2(config_file):
    ruamel_yaml = YAML()
    return ruamel_yaml.load(config_file)

def save2(ostream, yaml) -> None:
    ruamel_yaml = YAML()
    ruamel_yaml.dump(yaml, ostream)

def save_yaml(yaml, ostream) -> None:
    ruamel_yaml = YAML()
    ruamel_yaml.dump(yaml, ostream)

class Resource:

    name = None
    azure_resource = None

    def __init__(self, name, azure_resource):
        self.name = name
        self.azure_resource = azure_resource

    def __str__(self):
        return self.name

    def as_yaml(self):
        return azure_resource_as_yaml(self.azure_resource)

def load_resource_from_yaml(name, resource_yaml) -> Resource:
    return Resource(name, resource_yaml)

def azure_resource_as_yaml(azure_resource) -> dict:
    return azure_resource
