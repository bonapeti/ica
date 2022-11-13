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

def load2(config_file):
    ruamel_yaml = YAML()
    return ruamel_yaml.load(config_file)

def save2(ostream, yaml) -> None:
    ruamel_yaml = YAML()
    ruamel_yaml.dump(yaml, ostream)
