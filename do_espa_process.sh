#!/bin/sh -x

#export AWS_ACCESS_KEY_ID=XXXX
#export AWS_SECRET_ACCESS_KEY=XXXXX
export AWS_DEFAULT_REGION=us-west-2

pushd /efs/auxiliaries/aster
python -m SimpleHTTPServer 1666 &
pid=$!; echo "simple server pid $pid"
popd

export PYTHONPATH=/devel/daelf/espa-all/espa-processing/processing
export ESPA_CACHE_HOST_LIST=localhost
time espa-process --order-id toast \
	--product-type landsat \
	--output-format gtiff \
	--bridge-mode \
	--input-product-id LE07_L1TP_042034_20130104_20160909_01_T1 \
	--input-url s3://lsaa-level1-data/L7/2013/042/034/LE07_L1TP_042034_20130104_20160909_01_T1.tar.gz \
	--include-top-of-atmosphere \

kill $pid
