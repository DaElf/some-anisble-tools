#!/bin/sh -x

#export AWS_ACCESS_KEY_ID=XXXXX
#export AWS_SECRET_ACCESS_KEY=XXXXX
export AWS_DEFAULT_REGION=us-west-2
export SQSBatchQueue=mvp-demo-espa-ecs-batch-SQSBatchQueue-1SKDIKEAKXAHK.fifo

export ESPA_CACHE_HOST_LIST=localhost
export ESPA_CONFIG_PATH=$(pwd)

time python /usr/lib/python2.7/site-packages/espa_processing/espa_prybar.py \
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

