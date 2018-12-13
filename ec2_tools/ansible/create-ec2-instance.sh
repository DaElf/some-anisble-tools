#!/bin/sh

docker run --rm \
    -v $(pwd):/ansible/playbooks \
    -v ${HOME}/.aws:/root/.aws \
    --workdir $(pwd) \
    --env USER=${USER} \
    --env KEYPAIR=${KEYPAIR} \
    ansiblecm:2.6.4 \
    /ansible/playbooks/playbook_ec2.yml
