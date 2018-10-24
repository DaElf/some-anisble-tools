#!/bin/bash +x

export IPS_ALL_DIR=/devel/<YOUR-DEVEL-PATH>/ips-all
export IPS_QUEUE=ips2-devel-batch-ProcessJobQueueSpot
export IPS_JOBDEF=ips2-devel-batch-IPS_ProcessJob

$IPS_ALL_DIR/espa-container-tools/ips-local-testing/ips_submit_multi.py \
               --queue $IPS_QUEUE \
               --job-definition $IPS_JOBDEF \
               --input-bucket usgs-landsat \
               --prefix data/scene/l0rp/L08 \
               $1 
