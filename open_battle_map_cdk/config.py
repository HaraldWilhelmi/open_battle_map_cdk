from os.path import expanduser, join, isfile, dirname
from typing import Optional
from pydantic import BaseModel
from configparser import ConfigParser


class Config(BaseModel, ):
    name: str = 'obm'
    docker_dir: str = join(dirname(dirname(dirname(__file__))), 'open_battle_map', 'deploy', 'docker')


_config: Optional[Config] = None


def get_config_file_name() -> str:
    return join(expanduser('~'), '.open_battle_map_cdk')


def get_config():
    global _config
    if _config is None:
        file_name = get_config_file_name()
        if not isfile(file_name):
            raise Exception(f"Configuration file '{file_name}' is missing!")
        parser = ConfigParser()
        try:
            parser.read('FILE.INI')
            _config = Config(**parser['DEFAULT'].__dict__)
            if not isfile(join(_config.docker_dir, 'Dockerfile')):
                raise Exception(f"No file Dockerfile found in '{_config.docker_dir}'! "
                    + f"Is the [DEFAULT]/docker_dir setting correct in {file_name}?")
        except Exception as e:
            raise Exception(f"Failed to read '{file_name}': {str(e)}")
    return _config
