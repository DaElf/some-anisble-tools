docker run --rm \
    -v $(pwd):/ansible/playbooks \
    -v ${HOME}/.ssh:/root/.ssh \
    -v ${HOME}/.aws:/root/.aws ansiblecm:2.6.1 \
    -i /ansible/playbooks/hosts \
    /ansible/playbooks/playbook.yml \
    --extra-vars "privatekeyfilepath=/root/.ssh/${USER}.pem"
