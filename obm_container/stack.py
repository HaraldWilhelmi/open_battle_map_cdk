import aws_cdk as cdk
import aws_cdk.aws_ec2 as ec2
from constructs import Construct
from aws_cdk.aws_ecs import FargateTaskDefinition, FargateService, ContainerImage, EfsVolumeConfiguration, \
    ContainerDefinition, MountPoint, FargatePlatformVersion, PortMapping, AwsLogDriver

from common.link_stacks import get_vpc, get_cluster, get_file_system
from obm_cluster.config import get_cluster_config
from obm_container.config import get_container_config

DATA_VOLUME = 'obm_data'
HTTP_PORT = 80
HTTPS_PORT = 443
SSH_PORT = 22
NFS_PORT = 2049


class ObmContainerStack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        builder = _Builder(self)
        builder.do_it()


class _Builder:
    def __init__(self, stack: cdk.Stack):
        self._config = get_container_config()
        self._cluster_config = get_cluster_config()
        self._name = self._config.stack_name
        self._stack = stack

    def do_it(self):
        vpc = get_vpc(self._stack)
        cluster = get_cluster(self._stack, vpc)
        web_security_group = self.get_web_security_group(vpc)
        task_definition = self.get_task_definition(web_security_group)
        self.get_service(cluster, task_definition, web_security_group)

    def _tag_it(self, it):
        cdk.Tags.of(it).add(self._config.tag_key, self._config.tag_value)

    def get_web_security_group(self, vpc):
        security_group = ec2.SecurityGroup(
            self._stack,
            'obm_web',
            vpc=vpc,
            allow_all_outbound=True,
        )
        for port_number in [SSH_PORT, HTTP_PORT, HTTPS_PORT]:
            port = ec2.Port(
                from_port=port_number,
                to_port=port_number,
                protocol=ec2.Protocol.TCP,
                string_representation=f"Port {port_number}"
            )
            security_group.add_ingress_rule(peer=ec2.Peer.any_ipv4(), connection=port)
            security_group.add_ingress_rule(peer=ec2.Peer.any_ipv6(), connection=port)
        self._tag_it(security_group)
        return security_group

    def get_task_definition(self, security_group):
        task_definition = FargateTaskDefinition(self._stack, self._name, memory_limit_mib=512, cpu=256)
        task_definition.add_volume(name=DATA_VOLUME, efs_volume_configuration=self.get_volume(security_group))
        image = ContainerImage.from_asset(directory=self._config.docker_dir)
        container = ContainerDefinition(
            self._stack,
            'obm_container',
            task_definition=task_definition,
            image=image,
            environment=self.get_environment(),
            logging=AwsLogDriver(stream_prefix=self._config.service_name),
        )
        container.add_mount_points(self.get_mount_point())
        container.add_port_mappings(
            PortMapping(container_port=HTTP_PORT, host_port=HTTP_PORT),
            PortMapping(container_port=HTTPS_PORT, host_port=HTTPS_PORT),
            PortMapping(container_port=SSH_PORT, host_port=SSH_PORT),
        )
        self._tag_it(container)
        self._tag_it(task_definition)
        return task_definition

    def get_environment(self):
        if self._config.use_tls:
            tls_domain = self._config.service_name + '.' + self._cluster_config.domain
        else:
            tls_domain = 'unset'
        return {
            'TLS_DOMAIN': tls_domain,
            'LETSENCRYPT_URL': self._config.letsencrypt_url,
        }

    def get_volume(self, web_security_group):
        file_system = get_file_system(self._stack)
        file_system.connections.allow_default_port_from(web_security_group)
        volume = EfsVolumeConfiguration(file_system_id=file_system.file_system_id)
        return volume

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
            service_name=self._config.service_name,
            platform_version=FargatePlatformVersion.VERSION1_4,
            security_groups=[security_group],
            enable_ecs_managed_tags=True,
        )
        self._tag_it(service)
        return service
