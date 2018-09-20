docker run --rm \
    -v $(pwd):/ansible/playbooks \
    -v ${HOME}/.ssh:/root/.ssh \
    -v ${HOME}/.aws:/root/.aws ansiblecm \
    -i /ansible/playbooks/hosts \
    /ansible/playbooks/playbook.yml
