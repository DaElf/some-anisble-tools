#!/bin/sh -x

. /devel/cattelan/set_aws_cred.sh

export AWS_DEFAULT_REGION=us-west-2

export ESPA_CONFIG_PATH="$(pwd)"

my_dir="/jobtmp/$HOSTNAME"
mkdir -p $my_dir

#input="s3://landsat-pds/c1/L8/042/001/LC08_L1GT_042001_20170803_20170804_01_RT"

#input="s3://lsaa-level1-data/L8/2013/041/036/LC08_L1TP_041036_20130411_20170310_01_T1.tar.gz"
#prodid="LC08_L1TP_041036_20130411_20170310_01_T1"

#input="s3://lsaa-level1-data/L7/2013/042/034/LE07_L1TP_042034_20130104_20160909_01_T1.tar.gz"
#prodid="LE07_L1TP_042034_20130104_20160909_01_T1"
input="s3://lsaa-level1-data/L8/2013/042/034/LC08_L1TP_042034_20130327_20170310_01_T1.tar.gz"
prodid="LC08_L1TP_042034_20130327_20170310_01_T1"

espa_process=/devel/daelf/espa-all/espa-processing/processing/cli.py
#espa_process=espa-process

debug="--debug --dev-mode --dev-intermediate"
full=""
#full="--include-sr-evi --include-surface-temperature --include-surface-water-extent"

export PYTHONPATH=/devel/daelf/espa-all/espa-processing/processing
(cd $my_dir; time $espa_process \
     --order-id toast \
     --product-type landsat \
     --output-format gtiff \
     --bridge-mode \
     --input-product-id $prodid \
     --input-url $input \
     --dist-method s3 \
     --dist-s3-bucket a.out \
     --include-top-of-atmosphere \
     --include-brightness-temperature \
     --include-surface-reflectance \
     $full \
     $debug \
)
