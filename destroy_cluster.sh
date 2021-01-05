#!/bin/bash

set -e

cd "$( dirname "${BASH_SOURCE[0]}" )"


echo '#######################################################################'
echo '###'
echo "### OBM_CDK_CONGIG=$OBM_CDK_CONFIG"
echo "### OBM_AWS_COMMAND_PREFIX=$OBM_AWS_COMMAND_PREFIX" 
echo '###'
echo '#######################################################################'

echo 'Are yo really sure? This will also delete all persistent data including:'
echo ' * All Map Sets'
echo ' * TLS Keys and Certificate'
echo ' * Admin Secret'
echo 'Have you checked that you are using the right configuration?'
echo 'To confirm type: YES<RETURN>'

read answer
[[ $answer == YES ]] || exit 0

cdk synth
$OBM_AWS_COMMAND_PREFIX cdk destroy
