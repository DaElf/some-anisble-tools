echo "aws-devel-instance ansible_ssh_common_args='-o StrictHostKeyChecking=no' ansible_ssh_host=$(aws ec2 describe-instances --filter "Name=instance-state-name,Values=running,Name=tag:Name,Values=$USER-devel" --query "Reservations[].Instances[].[PublicIpAddress]" --output text)" > hosts

echo "jenkins-docker-worker ansible_ssh_common_args='-o StrictHostKeyChecking=no' ansible_ssh_host=$(aws ec2 describe-instances --filter "Name=instance-state-name,Values=running,Name=tag:Name,Values=dilley-dev-spot-host" --query "Reservations[].Instances[].[PublicDnsName]" --output text)"
