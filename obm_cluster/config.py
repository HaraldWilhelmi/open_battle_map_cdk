from sys import stderr
from typing import Optional
from pydantic import BaseModel, validator
from common.config import get_config_as_dict, get_config_file_name


class Config(BaseModel, ):
    # Required
    hosted_zone_id: str
    domain: str
    # Optional
    stack_name = 'ObmCluster'
    tag_key: str = 'application'
    tag_value: Optional[str]


_config: Optional[Config] = None


def get_cluster_config():
    global _config
    if _config is None:
        file_name = get_config_file_name('OBM_CDK_CLUSTER_CONFIG')
        try:
            as_dict = get_config_as_dict(file_name, 'CLUSTER')
            _config = Config(**as_dict)
        except Exception as e:
            print(f"Failed to read '{file_name}': {str(e)}!", file=stderr)
            exit(1)
        if _config.tag_value is None:
            _config.tag_value = _config.stack_name
    return _config
