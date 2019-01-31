#!/bin/sh

docker run --rm \
    -v $(pwd):/ansible/playbooks \
    -v ${HOME}/.aws:/root/.aws \
    --workdir $(pwd) \
    --env USER=${USER} \
    --env KEYPAIR=${KEYPAIR} \
    ansiblecm:2.6.4 \
    -i /ansible/playbooks/hosts \
    /ansible/playbooks/playbook_configure_ec2.yml
