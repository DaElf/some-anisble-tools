#!/bin/sh -x

my_id=$(cat image_id)
aws ec2 create-image --instance-id $my_id --name "ESPA_ProcessComputeStorageS3" --description "AMI for ESPA compute processing"
