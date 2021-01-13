from aws_cdk.aws_efs import FileSystem
from aws_cdk.core import Fn, Construct
from aws_cdk.aws_ec2 import Vpc, SecurityGroup
from aws_cdk.aws_ecs import Cluster

from obm_cluster.config import get_cluster_config
from obm_volume.config import get_volume_config


def get_vpc(scope: Construct) -> Vpc:
    config = get_cluster_config()
    stack_name = config.stack_name
    return Vpc.from_vpc_attributes(
        scope, 'vpc',
        vpc_id=Fn.import_value(stack_name + 'VpcId'),
        vpc_cidr_block=Fn.import_value(stack_name + 'VpcCidrBlock'),
        availability_zones=[
            Fn.import_value(stack_name + 'AvailabilityZone0'),
            Fn.import_value(stack_name + 'AvailabilityZone1'),
        ],
        public_subnet_ids=[
            Fn.import_value(stack_name + 'PublicSubnetId0'),
            Fn.import_value(stack_name + 'PublicSubnetId1'),
        ],
        isolated_subnet_ids=[
            Fn.import_value(stack_name + 'IsolatedSubnet0'),
            Fn.import_value(stack_name + 'IsolatedSubnet1'),
        ],
    )


def get_cluster(scope: Construct, vpc: Vpc) -> Cluster:
    config = get_cluster_config()
    stack_name = config.stack_name
    return Cluster.from_cluster_attributes(
        scope, 'cluster',
        cluster_name=Fn.import_value(stack_name + 'ClusterName'),
        vpc=vpc,
        has_ec2_capacity=False,
        security_groups=[],
    )


def get_file_system(scope: Construct) -> FileSystem:
    config = get_volume_config()
    stack_name = config.stack_name
    security_group = SecurityGroup.from_security_group_id(
        scope, 'nfs_security_group',
        security_group_id=Fn.import_value(stack_name + 'SecurityGroupId')
    )
    return FileSystem.from_file_system_attributes(
        scope, 'filesystem',
        file_system_id=Fn.import_value(stack_name + 'FileSystemId'),
        security_group=security_group
    )
