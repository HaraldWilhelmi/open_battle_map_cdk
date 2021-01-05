# Deploy Open Battle Map on AWS

## What is this?

This code is meant to deploy the Open Battle Map application for private use
in a *cost-efficient* way on Amazon Web Services. See also:

 * https://github.com/HaraldWilhelmi/open_battle_map

It is only separated from that code because it needs its own Python VirtualEnv
and PyCHarm does not like to have two of those in the same project.

## Quick Start

 * Prerequisites
   * You have an AWS account (certainly you have activated MFA and are using aws-vault... ?)
   * You have installed Amazon CDK and have at least a rough idea what it does.
   * You are a proud owner of a DNS domain, and you have either delegated a sub-domain
     to AWS Route 53, or the whole domain is registered via Route 53.
 * Do it
   * Check out this repository in the same parent, where you have checked out your copy
     of the open_battle_map repo.
   * Run ./deploy/prepare_build.sh in the other repository. Make sure that it terminates
     successfully.
   * Create a configuration file like draft below. The Zone ID is visible in the Hosted
     Zones overview page of Route 53:
    
            [DEFAULT]
            name = <the name of the thing>
            hosted_zone_id = <your Route 53 Zone ID>
            domain = <your Route 53 domain>
    
   * Export the following environment variables as you need them:
    
            OBM_AWS_COMMAND_PREFIX=aws-vault exec <your profile> --
            OBM_CDK_CONFIG=<your config file>
   * Run:
    
            ./setup_cluster.sh
    
   * Get the Admin Secret:
    
            ssh root@<the name of the thing>.<your Route 53 domain>
            # cat /data/obm_data/config
    
   * Have fun:
    
            https://<the name of the thing>.<your Route 53 domain>
    
## Dirty Details

For more configuration options have a look at `open_battle_map_cdk/config.py`.
Consider setting `tag_key`/`tag_value` to help you in the AWS Cost Explore.
Basically this setup consists of the following components:

 * A single ECS container with the application and nginx to TLS termination.
 * A data volume for all the persistent data (obm_data: config + Map Sets, tls:
   Keys and Certificate).
 * An AWS Lambda, which sets up DNS for your container, when it is started
   or replaced (see https://github.com/foby/aws-ecs-public-dns).
 * Letsencrypt supplies the TLS certificate. 

## Alternatives

For a more professional setup consider replacing the AWS Lambda to assign
the DNS name by AWS Application Load Balancer. For my private setup I considered
that option to be too costly.

Please note that a true cluster setup with multiple active application servers/containers
would also require some way to ensure that the data is not corrupted by parallel
access. The easiest way to do so would be to configure the load balancer to distribute
the work load based on the Map Set UUID.

## Credits

Many thanks to Andreas Pasch, who helped me (and maybe you too) to save 18 bucks
per month by *not* using an AWS ALB.

See https://github.com/foby/aws-ecs-public-dns for details.