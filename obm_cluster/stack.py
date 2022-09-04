from os.path import dirname, join

import aws_cdk as cdk
from constructs import Construct
import aws_cdk.aws_ec2 as ec2
from aws_cdk.aws_ecs import Cluster
from aws_cdk.aws_iam import PolicyStatement, Effect
from aws_cdk.aws_lambda import Function, Runtime, Code
from aws_cdk.aws_events import Rule as EventRule, EventPattern
from aws_cdk.aws_events_targets import LambdaFunction as LambdaEventTarget

from obm_cluster.config import get_cluster_config


MAX_AVAILABILITY_ZONES = 2


class ObmClusterStack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        builder = _Builder(self)
        builder.do_it()


class _Builder:
    def __init__(self, stack: cdk.Stack):
        self._config = get_cluster_config()
        self._name = self._config.stack_name
        self._stack = stack

    def do_it(self):
        self.deploy_aws_ecs_public_dns()
        vpc = self.get_vpc()
        self.get_cluster(vpc)

    def get_vpc(self):
        vpc = ec2.Vpc(
            self._stack, self._name + 'Vpc', cidr='10.0.0.0/16', nat_gateways=0, max_azs=MAX_AVAILABILITY_ZONES
        )
        self._export('VpcId', vpc.vpc_id)
        self._export('VpcCidrBlock', vpc.vpc_cidr_block)
        for i in range(MAX_AVAILABILITY_ZONES):
            self._export(f'AvailabilityZone{i}', vpc.availability_zones[i])
            self._export(f'PublicSubnetId{i}', vpc.public_subnets[i].subnet_id)
            self._export(f'IsolatedSubnet{i}', vpc.isolated_subnets[i].subnet_id)
        self._tag_it(vpc)
        return vpc

    def _export(self, name, value):
        cdk.CfnOutput(self._stack, name, value=value, export_name=self._name+name)

    def _tag_it(self, it):
        cdk.Tags.of(it).add(self._config.tag_key, self._config.tag_value)

    def get_cluster(self, vpc):
        cluster = Cluster(self._stack, self._name, vpc=vpc)
        cdk.Tags.of(cluster).add('hostedZoneId', self._config.hosted_zone_id)
        cdk.Tags.of(cluster).add('domain', self._config.domain)
        self._export('ClusterName', cluster.cluster_name)
        self._tag_it(cluster)
        return cluster

    def deploy_aws_ecs_public_dns(self):
        code_path = join(dirname(dirname(__file__)), 'build', 'aws-ecs-public-dns.zip')
        func = Function(
            self._stack,
            'public_dns',
            runtime=Runtime.NODEJS_16_X,
            handler='src/update-task-dns.handler',
            memory_size=128,
            code=Code.from_asset(path=code_path)
        )
        self._tag_it(func)
        func.add_to_role_policy(statement=self.get_public_dns_policy_statement())
        self.create_event_rule(func)

    def create_event_rule(self, func):
        event_pattern = EventPattern(
            source=['aws.ecs'],
            detail_type=['ECS Task State Change'],
            detail={
                'desiredStatus': ['RUNNING'],
                'lastStatus': ['RUNNING'],
            }
        )
        rule = EventRule(
            self._stack,
            'public_dns_rule',
            event_pattern=event_pattern,
            enabled=True,
        )

        event_target = LambdaEventTarget(handler=func)
        rule.add_target(event_target)
        self._tag_it(rule)

    @staticmethod
    def get_public_dns_policy_statement():
        statement = PolicyStatement(
            effect=Effect.ALLOW, actions=[
                "ec2:DescribeNetworkInterfaces",
                "ecs:DescribeClusters",
                "ecs:ListTagsForResource",
                "route53:ChangeResourceRecordSets",
            ],
            resources=['*'],
        )
        return statement
