from aws_cdk import core
from aws_cdk.aws_ec2 import SecurityGroup, Peer, Port, Protocol, Vpc
from aws_cdk.aws_ecs import FargateTaskDefinition, FargateService, Cluster, ContainerImage, EfsVolumeConfiguration, \
    ContainerDefinition, MountPoint, FargatePlatformVersion, PortMapping
from aws_cdk.aws_efs import FileSystem, LifecyclePolicy
from aws_cdk.core import Tags

from open_battle_map_cdk.config import get_config


DATA_VOLUME = 'obm_data'
HTTP_PORT = 80
HTTPS_PORT = 443
SSH_PORT = 22
NFS_PORT = 2049


class OpenBattleMapCdkStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        builder = OpenBattleMapBuilder(self)
        builder.do_it()


class OpenBattleMapBuilder:
    def __init__(self, stack: core.Stack):
        self._config = get_config()
        self._name = self._config.name
        self._stack = stack

    def do_it(self):
        vpc = self.get_vpc()
        cluster = self.get_cluster(vpc)
        web_security_group = self.get_web_security_group(vpc)
        task_definition = self.get_task_definition(vpc, web_security_group)
        self.get_service(cluster, task_definition, web_security_group)

    def get_vpc(self):
        vpc = Vpc(self._stack, self._name + '_vpc', cidr='10.0.0.0/16')
        self._tag_it(vpc)
        return vpc

    def _tag_it(self, it):
        Tags.of(it).add(self._config.tag_key, self._config.tag_value)

    def get_cluster(self, vpc):
        cluster = Cluster(self._stack, self._name + '_cluster', vpc=vpc)
        Tags.of(cluster).add('hostedZoneId', self._config.hosted_zone_id)
        Tags.of(cluster).add('domain', self._config.domain)
        self._tag_it(cluster)
        return cluster

    def get_web_security_group(self, vpc):
        security_group = SecurityGroup(
            self._stack,
            'obm_web',
            vpc=vpc,
            allow_all_outbound=True,
        )
        for port_number in [SSH_PORT, HTTP_PORT, HTTPS_PORT]:
            port = Port(
                from_port=port_number,
                to_port=port_number,
                protocol=Protocol.TCP,
                string_representation=f"Port {port_number}"
            )
            security_group.add_ingress_rule(peer=Peer.any_ipv4(), connection=port)
            security_group.add_ingress_rule(peer=Peer.any_ipv6(), connection=port)
        self._tag_it(security_group)
        return security_group

    def get_task_definition(self, vpc, security_group):
        task_definition = FargateTaskDefinition(self._stack, self._name, memory_limit_mib=512, cpu=256)
        task_definition.add_volume(name=DATA_VOLUME, efs_volume_configuration=self.get_volume(vpc, security_group))
        image = ContainerImage.from_asset(directory=self._config.docker_dir)
        container = ContainerDefinition(self._stack, 'obm_container', task_definition=task_definition, image=image)
        container.add_mount_points(self.get_mount_point())
        container.add_port_mappings(
            PortMapping(container_port=HTTP_PORT, host_port=HTTP_PORT),
            PortMapping(container_port=HTTPS_PORT, host_port=HTTPS_PORT),
            PortMapping(container_port=SSH_PORT, host_port=SSH_PORT),
        )
        self._tag_it(container)
        self._tag_it(task_definition)
        return task_definition

    def get_volume(self, vpc, web_security_group):
        nfs_security_group = self.get_nfs_security_group(web_security_group, vpc)

        file_system = FileSystem(
            self._stack,
            'obm_data_volume',
            vpc=vpc,
            lifecycle_policy=LifecyclePolicy.AFTER_90_DAYS,
            security_group=nfs_security_group,
        )
        self._tag_it(file_system)
        volume = EfsVolumeConfiguration(file_system_id=file_system.file_system_id)
        return volume

    def get_nfs_security_group(self, web_security_group, vpc):
        nfs_security_group = SecurityGroup(
            self._stack,
            'obm_efs',
            vpc=vpc,
            allow_all_outbound=True,
        )
        port = Port(
            from_port=NFS_PORT,
            to_port=NFS_PORT,
            protocol=Protocol.TCP,
            string_representation='NFS')
        nfs_security_group.add_ingress_rule(peer=web_security_group, connection=port)
        self._tag_it(nfs_security_group)
        return nfs_security_group

    @staticmethod
    def get_mount_point():
        return MountPoint(container_path='/data', source_volume=DATA_VOLUME, read_only=False)

    def get_service(self, cluster, task_definition, security_group):
        service = FargateService(
            self._stack,
            'obm_service',
            cluster=cluster,
            task_definition=task_definition,
            assign_public_ip=True,
            service_name='obm',
            platform_version=FargatePlatformVersion.VERSION1_4,
            security_groups=[security_group],
        )
        self._tag_it(service)
        return service
