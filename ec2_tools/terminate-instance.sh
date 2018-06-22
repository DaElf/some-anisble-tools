#!/bin/sh
aws --profile default --region us-west-2 ec2 terminate-instances --instance-ids $(cat image_id)
