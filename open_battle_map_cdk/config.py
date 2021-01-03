from os.path import expanduser, join, isfile, dirname
from sys import stderr
from typing import Optional
from pydantic import BaseModel
from configparser import ConfigParser


class Config(BaseModel, ):
    name: str = 'obm'
    docker_dir: str = join(dirname(dirname(dirname(__file__))), 'open_battle_map', 'deploy', 'docker')
    hosted_zone_id: str
    domain: str
    tag_key: str = 'application'
    tag_value: Optional[str]


_config: Optional[Config] = None


def get_config_file_name() -> str:
    return join(expanduser('~'), '.open_battle_map_cdk')


def get_config():
    global _config
    if _config is None:
        file_name = get_config_file_name()
        try:
            if not isfile(file_name):
                raise Exception(f"Configuration file '{file_name}' is missing!")
            parser = ConfigParser()
            parser.read(file_name)
            _config = Config(
                **{key: value
                   for key, value in parser['DEFAULT'].items()
                   }
            )
            if _config.tag_value is None:
                _config.tag_value = _config.name
            if not isfile(join(_config.docker_dir, 'Dockerfile')):
                raise Exception(f"No file Dockerfile found in '{_config.docker_dir}'! "
                                + f"Is the [DEFAULT]/docker_dir setting correct in {file_name}?")
        except Exception as e:
            print(f"Failed to read '{file_name}': {str(e)}", file=stderr)
            exit(1)
    return _config
