#!/bin/bash

set -e

cd "$( dirname "${BASH_SOURCE[0]}" )"

rm -rf aws-ecs-public-dns
git clone https://github.com/foby/aws-ecs-public-dns.git

mkdir -p build
(
    cd aws-ecs-public-dns
    npm install
    zip -r ../build/aws-ecs-public-dns.zip src node_modules -x .serverless
)

echo '#######################################################################'
echo '###'
echo "### OBM_CDK_CONGIG=$OBM_CDK_CONFIG"
echo "### OBM_AWS_COMMAND_PREFIX=$OBM_AWS_COMMAND_PREFIX" 
echo '###'
echo '#######################################################################'


cdk synth
$OBM_AWS_COMMAND_PREFIX cdk deploy

