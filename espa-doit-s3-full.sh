#!/bin/sh -x

my_dir=$(dirname "$0")

cd $my_dir
export ESPA_CONFIG_PATH=$my_dir

gpg --import ./gpg-tools/USGS_private.gpg || true
export PYTHONPATH=/efs/daelf/espa-all/espa-processing/processing

time /efs/daelf/espa-all/espa-processing/processing/cli.py \
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
