#!/bin/sh

# Global Settings
account="default"
region="us-west-2"

# Instance settings
# This is normal image with ec2-user == 1000
image_id="ami-0ad99772"
#image_id="ami-0a3c7372"
# computer image for batch
#image_id="ami-e06e1f98"

ssh_key_name="daelf-us-west-2"
security_group_id="sg-f07ea081"
security_group="daelf-data0-fw"
instance_type="c3.xlarge"
vpc_id="vpc-f0114a96"
subnet_id="subnet-d7d86b9c"
root_vol_size=20
count=1

# Tags
tags_Name="daelf-instance"
tags_Owner="daelf"
tags_ApplicationRole="Dev"
tags_Cluster="DaElf AMI"
tags_Environment="dev"
tags_OwnerEmail="cattelan@digitalelves.com"
tags_Project="Test"
tags_BusinessUnit="Cloud Platform Engineering"
tags_SupportEmail="cattelan@digitalelves.com"

rm -f ./image_id
echo 'creating instance...'
set -x
id=$(aws --profile $account --region $region ec2 run-instances \
	 --associate-public-ip-address \
	 --image-id $image_id \
	 --count $count \
	 --instance-type $instance_type \
	 --key-name $ssh_key_name \
	 --security-group-id $security_group_id \
	 --subnet-id $subnet_id \
	 --query 'Instances[*].InstanceId' --output text)

#--block-device-mapping "[ { \"DeviceName\": \"/dev/sda1\", \"Ebs\": { \"VolumeSize\": $root_vol_size } } ]" \


set +x
echo "$id created"
echo "$id" > image_id
# tag it

echo "tagging $id..."

aws --profile $account --region $region ec2 create-tags \
    --resources $id \
    --tags \
    Key=Name,Value="$tags_Name" \
    Key=Owner,Value="$tags_Owner"  \
    Key=ApplicationRole,Value="$tags_ApplicationRole" \
    Key=Cluster,Value="$tags_Cluster" \
    Key=Environment,Value="$tags_Environment" \
    Key=OwnerEmail,Value="$tags_OwnerEmail" \
    Key=Project,Value="$tags_Project" \
    Key=BusinessUnit,Value="$tags_BusinessUnit" \
    Key=SupportEmail,Value="$tags_SupportEmail" \
    Key=OwnerGroups,Value="$tags_OwnerGroups"

echo "storing instance details..."
# store the data
aws --profile $account --region $region ec2 describe-instances --instance-id $id --query 'Reservations[].Instances[].PublicDnsName' --output text
aws --profile $account --region $region ec2 describe-instances --instance-ids $id > instance-details.json

