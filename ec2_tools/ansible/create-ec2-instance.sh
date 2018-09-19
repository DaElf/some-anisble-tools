docker run --rm \
    -v $(pwd):/ansible/playbooks \
    -v ${HOME}/.aws:/root/.aws \
    ansiblecm:2.6.1 \
    /ansible/playbooks/playbook_ec2.yml \
    --extra-vars "keyfilename=${USER} keyfilepath=~/.ssh/${USER} nametag=${USER}-dev-spot-host"
