from os.path import join, isfile, dirname, expanduser
from os import environ
from sys import stderr
from typing import Optional
from pydantic import BaseModel, validator
from configparser import ConfigParser

from common.config import get_config_file_name, get_config_as_dict


class Config(BaseModel, ):
    stack_name: str = 'ObmContainer'
    service_name: str = 'obm'
    docker_dir: str = join(dirname(dirname(dirname(__file__))), 'open_battle_map', 'deploy', 'docker')
    tag_key: str = 'application'
    tag_value: Optional[str] = None
    letsencrypt_url: str = 'https://acme-v02.api.letsencrypt.org/directory'
    use_tls: bool = True


_config: Optional[Config] = None


def get_container_config():
    global _config
    if _config is None:
        file_name = get_config_file_name('OBM_CDK_CONTAINER_CONFIG')
        try:
            as_dict = get_config_as_dict(file_name, 'CONTAINER')
            _config = Config(**as_dict)
        except Exception as e:
            print(f"Failed to read '{file_name}': {str(e)} - using defaults.", file=stderr)
            _config = Config()
        if _config.tag_value is None:
            _config.tag_value = _config.stack_name
        if not isfile(join(_config.docker_dir, 'Dockerfile')):
            raise Exception(f"No file Dockerfile found in '{_config.docker_dir}'! "
                            + f"Is the [CONTAINER]/docker_dir setting correct in {file_name}?")
    return _config
