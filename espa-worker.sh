#!/bin/sh -x

pushd /efs/auxiliaries/aster
python -m SimpleHTTPServer 1666 &
pid=$!; echo "simple server pid $pid"
popd

gpg --import USGS_private.gpg || true
export ESPA_CONFIG_PATH=$(pwd)
export SQSBatchQueue=mvp2-espa-ecs-batch-SQSBatchQueue-1WKH30SU1TQN3.fifo
export AWS_DEFAULT_REGION=us-west-2
espa-worker

kill $pid
