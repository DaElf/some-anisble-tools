#!/bin/sh -x

pushd /efs/auxiliaries/aster
python -m SimpleHTTPServer 1666 &
pid=$!; echo "simple server pid $pid"
popd

export ESPA_CONFIG_PATH=$(pwd)
espa-process --order-id toast \
	--product-type landsat \
	--input-product-id LC08_L1TP_047027_20131014_20170308_01_T1 \
	--input-url file:///efs/DATA/LC08_L1TP_047027_20131014_20170308_01_T1.tar.gz \
	--bridge-mode \
	--output-format gtiff \
\
	--include-top-of-atmosphere \
	--include-brightness-temperature \
	--include-surface-reflectance \
	--include-surface-temperature \
	--include-sr-evi \
\
	--include-cfmask \
	--include-pixel-qa \
	--include-customized-source-data \
	--include-sr-evi \
	--include-sr-msavi \
	--include-sr-nbr \
	--include-sr-nbr2 \
	--include-sr-ndmi \
	--include-sr-ndvi \
	--include-sr-savi \
	--include-surface-water-extent \
	--include-statistics \

kill $pid
