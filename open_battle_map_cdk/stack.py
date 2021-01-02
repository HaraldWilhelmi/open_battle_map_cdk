from aws_cdk import core
from aws_cdk.aws_ec2 import SecurityGroup, Peer, Port, Protocol, Vpc
from aws_cdk.aws_ecs import FargateTaskDefinition, FargateService, Cluster, ContainerImage, EfsVolumeConfiguration, \
    ContainerDefinition, MountPoint, FargatePlatformVersion, PortMapping
from aws_cdk.aws_efs import FileSystem, LifecyclePolicy

from open_battle_map_cdk.config import get_config


DATA_VOLUME = 'obm_data'
EXPOSED_PORT = 80
SSH_PORT = 22
NFS_PORT = 2049


class OpenBattleMapCdkStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        config = get_config()
        vpc = Vpc(self, config.name + '_vpc', cidr='10.0.0.0/16')
        cluster = Cluster(self, config.name + '_cluster', vpc=vpc)
        security_group = self.get_web_security_group(vpc)
        task_definition = self.get_task_definition(vpc, security_group, config)

        FargateService(
            self,
            'obm_service',
            cluster=cluster,
            task_definition=task_definition,
            assign_public_ip=True,
            service_name='obm',
            platform_version=FargatePlatformVersion.VERSION1_4,
            security_groups=[security_group],
        )

    def get_web_security_group(self, vpc):
        security_group = SecurityGroup(
            self,
            'obm_web',
            vpc=vpc,
            allow_all_outbound=True,
        )
        for port_number in [SSH_PORT, EXPOSED_PORT]:
            port = Port(
                from_port=port_number,
                to_port=port_number,
                protocol=Protocol.TCP,
                string_representation=f"Port {port_number}"
            )
            security_group.add_ingress_rule(peer=Peer.any_ipv4(), connection=port)
            security_group.add_ingress_rule(peer=Peer.any_ipv6(), connection=port)
        return security_group

    def get_task_definition(self, vpc, security_group, config):
        task_definition = FargateTaskDefinition(self, config.name, memory_limit_mib=512, cpu=256)
        task_definition.add_volume(name=DATA_VOLUME, efs_volume_configuration=self.get_volume(vpc, security_group))
        image = ContainerImage.from_asset(directory=config.docker_dir)
        container = ContainerDefinition(self, 'obm_container', task_definition=task_definition, image=image)
        container.add_mount_points(self.get_mount_point())
        container.add_port_mappings(
            PortMapping(container_port=EXPOSED_PORT, host_port=EXPOSED_PORT),
            PortMapping(container_port=SSH_PORT, host_port=SSH_PORT),
        )
        return task_definition

    def get_volume(self, vpc, security_group):
        nfs_security_group = SecurityGroup(
            self,
            'obm_efs',
            vpc=vpc,
            allow_all_outbound=True,
        )
        port = Port(
            from_port=NFS_PORT,
            to_port=NFS_PORT,
            protocol=Protocol.TCP,
            string_representation='NFS')
        nfs_security_group.add_ingress_rule(peer=security_group, connection=port)

        file_system = FileSystem(
            self,
            'obm_data_volume',
            vpc=vpc,
            lifecycle_policy=LifecyclePolicy.AFTER_90_DAYS,
            security_group=nfs_security_group,
        )
        return EfsVolumeConfiguration(file_system_id=file_system.file_system_id)

    @staticmethod
    def get_mount_point():
        return MountPoint(container_path='/data', source_volume=DATA_VOLUME, read_only=False)
