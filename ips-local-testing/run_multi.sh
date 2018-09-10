#!/bin/bash +x

export IPS_ALL_DIR=/devel/djt/ips-all
export IPS_QUEUE=djt-batch-IPS_ProcessJobQueueSpot
export IPS_JOBDEF=djt-batch-IPS_ProcessJob

$IPS_ALL_DIR/espa-container-tools/ips-local-testing/ips_submit_multi.py \
               --queue $IPS_QUEUE \
               --job-definition $IPS_JOBDEF \
               --input-bucket dev-lsds-l8-test-l0rp \
               --job-bucket jdc-test-dev \
               $1 
