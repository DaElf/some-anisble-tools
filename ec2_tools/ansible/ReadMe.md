This could be more complete but for now this the way to build a devel
instance

Edit the playbook_ec2.yml file changing following variables.
t2.small is probably fine for most things, building rpm's etc might
want t2.large

instance_type: t2.small
keypair: daelf-us-west-2 # pem file name
ansible_ssh_private_key_file: ~/Dropbox/USGS/daelf-us-west-2.pem
my_tag: daelf-ansible-devel

% ansible-playbook playbook_ec2.yml

The above cmd will create an ec2 instance with a public ip.
Look for this message with the ip address.

TASK [ec2-instance : debug] 
ok: [localhost] => {
    "ec2_provision_result.instances[0].public_ip": "34.219.187.199"
}
 
Add the ip to a hosts file eg.

% echo "aws-devel-instance ansible_ssh_host=34.219.187.199" > hosts

Edit the playbook.yml file and change the added user to your own
values, and run the playbook to config the instance.

Note if you have an existing instance just put the ip address in to
the hosts file and run the playbook.yml


% ansible-playbook -v  -i hosts playbook.yml
