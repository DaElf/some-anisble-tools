#!/bin/sh
set -e
set -x

. ./dofoo.sh

pushd /s3/auxiliaries/aster
python -m SimpleHTTPServer 1666 &
pid=$!; echo "simple server pid $pid"
popd

gpg --import ./gpg-tools/USGS_private.gpg || true
export ESPA_CACHE_HOST_LIST=localhost
export ESPA_CONFIG_PATH=$(pwd)
export PYTHONPATH=/devel/daelf/espa-all/espa-processing/processing

TOAST=0
  	#--include-surface-temperature \
	#--include-surface-water-extent \
#

(for JOB in `cat ./joblist.txt`; do
    JOBINPUTURL="s3://lsaa-level1-data/L7/2013/042/034/"$JOB".tar.gz"
    echo "time /devel/daelf/espa-all/espa-processing/processing/cli.py \
	--order-id toast$TOAST \
        --product-type landsat \
	--dist-method s3 \
  	--input-product-id $JOB \
  	--output-format gtiff \
  	--include-top-of-atmosphere \
  	--include-brightness-temperature \
  	--include-surface-reflectance \
  	--include-surface-temperature \
	--include-surface-water-extent \
  	--bridge-mode \
	--dev-mode \
  	--input-url $JOBINPUTURL"
    TOAST=`expr $TOAST + 1`
 done) | parallel --max-procs 2 --progress --verbose

export UNIQID=`date +%s`
kill $pid
