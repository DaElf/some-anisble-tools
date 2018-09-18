#!/bin/bash -x

# Usage:
# 1) Set the environment variables below to match your environment/directories
# 2) run_multi.sh ###, where ### is the number of scenes to process
# 3) Check your batch status and/or the L2 output S3 bucket for results

SQSHOME=.
export espaQueue=test-vpc-Batch-ProcessJobQueueSpot
export espaJobBucket=jdc-test-dev
export espaJobDefinition=test-vpc-Batch-ESPA_ProcessJob
export AWSRegion=us-west-2
export ESPA_PROCESS_TEMPLATE=$SQSHOME/espa-processing/processing/order_template.json
export ESPA_CONFIG_PATH=$SQSHOME/espa-container-tools/

export PYTHONPATH=$SQSHOME/espa-container-tools/SQS:$SQSHOME/espa-processing/processing
export PATH=$PATH:$PYTHONPATH

$SQSHOME/espa-container-tools/SQS/submit_array.py \
	--input-job-file $SQSHOME/espa-container-tools/SQS/jenkins_scenelist.txt \
        --full \
        $1

