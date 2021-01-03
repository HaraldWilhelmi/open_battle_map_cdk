#!/bin/bash

set -e

cd "$( dirname "${BASH_SOURCE[0]}" )"

rm -rf aws-ecs-public-dns
git clone https://github.com/foby/aws-ecs-public-dns.git

cd aws-ecs-public-dns
npm install

mkdir -p build
(
    cd aws-ecs-public-dns
    zip -r ../build/aws-ecs-public-dns.zip src node_modules -x .serverless
)
