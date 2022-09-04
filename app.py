#!/usr/bin/env python3
import os

import aws_cdk as cdk

from obm_cluster.config import get_cluster_config
from obm_container.config import get_container_config
from obm_volume.config import get_volume_config
from obm_cluster.stack import ObmClusterStack
from obm_volume.stack import ObmVolumeStack
from obm_container.stack import ObmContainerStack

cluster_config = get_cluster_config()
volume_config = get_volume_config()
container_config = get_container_config()

app = cdk.App()

cluster = ObmClusterStack(app, cluster_config.stack_name)
volume = ObmVolumeStack(app, volume_config.stack_name)
volume.add_dependency(cluster)
container = ObmContainerStack(app, container_config.stack_name)
container.add_dependency(volume)

app.synth()
