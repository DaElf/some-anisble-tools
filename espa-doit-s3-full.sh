#!/bin/sh -x

pushd /efs/auxiliaries/aster
python -m SimpleHTTPServer 1666 &
pid=$!; echo "simple server pid $pid"
popd

export AWS_ACCESS_KEY_ID=XXXXX
export AWS_SECRET_ACCESS_KEY=XXXXXX
export AWS_DEFAULT_REGION=us-west-2

#export PYTHONPATH=/devel/daelf/espa-all/espa-processing/processing
export ESPA_CACHE_HOST_LIST=localhost
export ESPA_CONFIG_PATH=$(pwd)

#time python /devel/daelf/espa-all/espa-processing/processing/espa-prybar.py \
time espa-process --order-id toast \
	--order-id toast \
	--product-type landsat \
	--input-product-id LE07_L1TP_042034_20130104_20160909_01_T1 \
	--input-url s3://lsaa-level1-data/L7/2013/042/034/LE07_L1TP_042034_20130104_20160909_01_T1.tar.gz \
        --dist-method s3 \
	--bridge-mode \
	--output-format gtiff \
\
	--include-top-of-atmosphere \
	--include-brightness-temperature \
	--include-surface-reflectance \
	--include-surface-temperature \
	--include-surface-water-extent \
\

kill $pid
