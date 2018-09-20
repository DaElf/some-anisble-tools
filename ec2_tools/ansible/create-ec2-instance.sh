docker run --rm \
    -v $(pwd):/ansible/playbooks \
    -v ${HOME}/.aws:/root/.aws \
    ansiblecm \
    /ansible/playbooks/playbook_ec2.yml
