#!/usr/bin/env python3

from aws_cdk import core

from open_battle_map_cdk.open_battle_map_cdk_stack import OpenBattleMapCdkStack


app = core.App()
OpenBattleMapCdkStack(app, "open-battle-map-cdk")

app.synth()
