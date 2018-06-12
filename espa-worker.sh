#!/bin/sh -x

pushd /efs/auxiliaries/aster
python -m SimpleHTTPServer 1666 &
pid=$!; echo "simple server pid $pid"
popd

gpg --import USGS_private.gpg
export ESPA_CONFIG_PATH=$(pwd)
export SQSBatchQueue=daelf-espa-SQSBatchQueue-429LS06UBLZ0.fifo
export AWS_DEFAULT_REGION=us-west-2

python /usr/lib/python2.7/site-packages/espa_processing/espa-worker.py

kill $pid
