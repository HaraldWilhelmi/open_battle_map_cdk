from os.path import join, isfile, dirname, expanduser
from os import environ
from sys import stderr
from typing import Optional
from pydantic import BaseModel
from configparser import ConfigParser

from common.config import get_config_file_name, get_config_as_dict


class Config(BaseModel, ):
    stack_name: str = 'ObmVolume'
    volume_name: str = 'obm_data'
    tag_key: str = 'application'
    tag_value: Optional[str] = None


_config: Optional[Config] = None


def get_volume_config():
    global _config
    if _config is None:
        file_name = get_config_file_name('OBM_CDK_CONTAINER_CONFIG')
        try:
            as_dict = get_config_as_dict(file_name, 'VOLUME')
            _config = Config(**as_dict)
        except Exception as e:
            print(f"Failed to read '{file_name}': {str(e)} - using defaults.", file=stderr)
            _config = Config()
        if _config.tag_value is None:
            _config.tag_value = _config.stack_name
    return _config
