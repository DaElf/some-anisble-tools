#!/bin/sh -x

my_id=$(cat image_id)
aws ec2 create-image --instance-id $my_id --name "daelf-compute-04" --description "AMI for ESPA compute processing"
