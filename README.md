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
   * Create the configuration file ~/.obm_cdk_config with at least lines given below.
     The Zone ID is visible in the Hosted Zones overview page of Route 53:
    
            [CLUSTER]
            hosted_zone_id = <your Route 53 Zone ID>
            domain = <your Route 53 domain>
    
   * Export the following environment variable as you need (example for aws-vault users):
    
            export OBM_AWS_COMMAND_PREFIX=aws-vault exec <your profile> --
 
   * Run:
    
            ./setup_everything.sh
    
   * Get the Admin Secret:
    
            ssh root@<the name of the thing>.<your Route 53 domain>
            # cat /data/obm_data/config
    
   * Have fun:
    
            https://obm.<your Route 53 domain>
    
## Dirty Details

### General Setup

If you followed the Quick Start instructions you got three Cloudformation Stacks:

 * ObmCluster: A VPC, a ECS Cluster, and Lambda which assigns public DNS names to
   freshly deployed containers. The trick with this setup is, that it comes
   without load balancers and NAT gateways. This reduces costs dramatically.
 * ObmVolume: A separate Stack with the volume for the dynamic data and its security
   group. Theoretically we could place the volume in the same volume group as the
   container because it will not be destroyed on destruction of the Stack.
   However, it's security group would - and  presently CDK is not able to import
   an EFS volume without a security group. So I found it easier and safer to
   put it into a separate stack. 
 * ObmContainer: The stack with the actual Docker Container.

These containers are coupled by Cloudformation Outputs. Nobody depends on the Container
Stack. That one can safely be destroyed without destroying your data or tempering with
the cluster, which may run other containers.

### Configuration Files

That is all controlled by two configuration files, which both default to the same path
`~/.obm_cdk_config`. If you need to separate them or just have more than one setup to
maintain, you may define the following environment variables:

 * OBM_CDK_CLUSTER_CONFIG: Points to the configuration file for the Cluster Stack.
   The file should contain a `[CLUSTER]` section - like the one from the
   Quick Start instructions.
 * OBM_CDK_CONTAINER_CONFIG: Used for the other two stacks. The file should contain
   a `[VOLUME]` and a `[CONTAINER]` section.

This setup allows you to have more than one OBM containers, which may or may not
share the same cluster. You just have to ensure that:

 1. You have one cluster configuration file for each cluster.
    
 2. You have one container configuration file for each Open Battle Map instance
    (volume+container).
    
 3. You defined in each section (CLUSTER/VOLUME/CONTAINER) a unique 'stack_name'.

 4. All the Open Battle Map instances have a unique 'service_name' (CONTAINER section).


### Common Configuration Parameters

Each of the configuration sections may have the following parameters:

 * **stack_name**: Name of the Cloud Formation Stack defined by this piece of
   configuration Defaults: ObmCluster/ObmVolume/ObmContainer.
 * **tag_key**: Name of tag the resource of the stack will be marked this.
   This tag is useful to find your way through the AWS Cost Explorer.
   To actually use the tag there, you need to activate it in the Billing
   Dashboard. (Default: application).
 * **tag_value**: The value to set the above Tag. Default: The name of the stack.

### Cluster Configuration

The cluster section has the following parameters:

 * **hosted_zone_id**: The ID of the AWS Route 53 Zone to be used for registration
   of the DNS name. Required - no default.
 * **domain**: The DNS domain belonging to the AWS Route 53 Zone. Required - no default.

### Volume Configuration

 * **volume_name**: Name of the volume. Default: obm_data.

### Container Configuration

 * **service_name**: Name of the service, which is created by the container. This
   name will be combined with the domain from the Cluster Configuration to create
   the DNS name.
 * **docker_dir**: The place the Dockerfile for the image will be searched for.
   By default, it will be assumed that the open_battle_map repository is checked
   out in the same parent directory as this repository.
 * **letsencrypt_url**: The URL used to contact Lets Encrypt. If you need to test
   TLS related stuff, please switch to their staging environment
   https://acme-staging-v02.api.letsencrypt.org/directory. Otherwise, you will quickly
   hit the rate limit. Default: https://acme-v02.api.letsencrypt.org/directory'
 * **use_tls**: This option allows you to switch of TLS. This is useful to recover
   a container form backup without revoking the old certificates:
   
    * Create new Container Stack with use_tls=False
    * Ssh to new container to unpack your backup to /data,
    * Re-run CDK with use_tls=True 
  
   Default: True

### Clean Up

If you want to remove the setup need to destroy the Stack in this order:

        cdk destroy <Container Stack>
        cdk destroy <Volume Stack>
        cdk destroy <Cluster Stack>

You may have to prefix your commands with your `OBM_AWS_COMMAND_PREFIX` to make them work.
This will not delete any volumes. Best check manually in the AWS Web GUI. Search for EFS.

## Alternatives

For a more professional setup consider replacing the AWS Lambda to assign
the DNS name by AWS Application Load Balancer. For my private setup I considered
that option to be too costly.

Please note that a true cluster setup with multiple active application servers/containers
would also require some way to ensure that the data is not corrupted by parallel
access. The easiest way to do so would be to configure the load balancer to distribute
the work load based on the Map Set UUID.

## Copyright

This software was written by Harald Wilhelmi. It may be used and distributed
under the terms of the GNU GENERAL PUBLIC LICENSE Version 3.

## Credits

Many thanks to Andreas Pasch, who helped me (and maybe you too) to save 18 bucks
per month by *not* using an AWS ALB.

See https://github.com/foby/aws-ecs-public-dns for details.