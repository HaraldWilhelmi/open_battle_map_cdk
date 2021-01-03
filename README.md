# Deploy Open Battle Map on AWS

## What is this?

This code is meant to deploy the Open Battle Map application for private use
in a *cost-efficient* way on Amazon Web Services. See also:

 * https://github.com/HaraldWilhelmi/open_battle_map

It is only separated from that code because it needs its own Python VirtualEnv
and PyCHarm does not like to have two of those in the same project.

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