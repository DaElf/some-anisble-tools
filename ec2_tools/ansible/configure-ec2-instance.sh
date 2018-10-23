#!/bin/sh

docker run --rm \
    -v $(pwd):/ansible/playbooks \
    -v ${HOME}/.ssh:/root/.ssh \
    -v ${HOME}/.aws:/root/.aws \
    --workdir $(pwd) \
    --env USER=${USER} \
    ansiblecm:2.6.4 \
    -i /ansible/playbooks/hosts \
    /ansible/playbooks/playbook.yml
