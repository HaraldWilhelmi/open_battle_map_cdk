#!/usr/bin/env python3

from aws_cdk import core

from open_battle_map_cdk.stack import OpenBattleMapCdkStack
from open_battle_map_cdk.config import get_config


app = core.App()
config = get_config()
OpenBattleMapCdkStack(app, config.name)

app.synth()
