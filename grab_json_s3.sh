#!/bin/sh -x

export AWS_DEFAULT_REGION=us-west-2
my_dir=$(dirname "$0")

cd $my_dir
export ESPA_CONFIG_PATH=$my_dir

gpg --import ./gpg-tools/USGS_private.gpg || true
export PYTHONPATH=/efs/daelf/espa-all/espa-processing/processing

time /efs/daelf/espa-all/espa-processing/processing/espa_batch_worker.py $1
ret=$?

echo "batchworker exit $ret"
exit $ret
