#!/bin/sh

docker run --rm \
    -v $(pwd):/ansible/playbooks \
    -v ${HOME}/.aws:/root/.aws \
    --workdir $(pwd) \
    ansiblecm \
    /ansible/playbooks/playbook_ec2.yml
