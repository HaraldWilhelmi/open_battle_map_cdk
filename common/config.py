from os.path import isfile, expanduser
from os import environ
from configparser import ConfigParser
from typing import Dict


def get_config_file_name(config_file_env_variable: str) -> str:
    candidate = environ.get(config_file_env_variable)
    if candidate is None or candidate == '':
        candidate = expanduser('~/.obm_cdk_config')
    return candidate


def get_config_as_dict(file_name: str, section: str) -> Dict[str, str]:
    if not isfile(file_name):
        raise Exception(f"Configuration file '{file_name}' is missing!")
    parser = ConfigParser()
    parser.read(file_name)
    return {
        key: value
        for key, value in parser[section].items()
    }