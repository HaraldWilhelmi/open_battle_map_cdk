import aws_cdk as cdk
import aws_cdk.aws_ec2 as ec2
from constructs import Construct
from aws_cdk.aws_efs import FileSystem, LifecyclePolicy

from common.link_stacks import get_vpc
from obm_volume.config import get_volume_config


class ObmVolumeStack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        builder = _Builder(self)
        builder.do_it()


class _Builder:
    def __init__(self, stack: cdk.Stack):
        self._config = get_volume_config()
        self._stack = stack

    def do_it(self):
        vpc = get_vpc(self._stack)
        nfs_security_group = self.get_nfs_security_group(vpc)
        file_system = FileSystem(
            self._stack,
            self._config.volume_name,
            vpc=vpc,
            security_group=nfs_security_group,
            lifecycle_policy=LifecyclePolicy.AFTER_90_DAYS,
        )
        self._export('FileSystemId', file_system.file_system_id)
        self._export('SecurityGroupId', nfs_security_group.security_group_id)
        self._tag_it(file_system)
        return file_system

    def _tag_it(self, it):
        cdk.Tags.of(it).add(self._config.tag_key, self._config.tag_value)

    def _export(self, name, value):
        cdk.CfnOutput(self._stack, name, value=value, export_name=self._config.stack_name+name)

    def get_nfs_security_group(self, vpc):
        nfs_security_group = ec2.SecurityGroup(
            self._stack,
            'obm_efs',
            vpc=vpc,
            allow_all_outbound=True,
        )
        self._tag_it(nfs_security_group)
        return nfs_security_group
