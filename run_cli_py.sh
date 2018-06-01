#!/bin/sh
set -e
#set -x

cd /efs/DEMO
mkdir -p /home/espa/.usgs/espa
chown -R espa /home/espa/.usgs/espa
mkdir -p /jobtmp
cp ./processing.conf /home/espa/.usgs/espa/processing.conf

TOAST=0
export JOBLIST=./joblist.txt

(for JOBSPEC in `cat $JOBLIST`
do
  #echo $JOBSPEC
  #echo $JOBLONG
  
  # Append JOBSPEC with the filename
  JOBLONG=$JOBSPEC".tar.gz"
  JOBINPUTURL="file:///efs/input/L8/"$JOBLONG
  echo "time cli.py --order-id toast$TOAST \
  	--product-type landsat \
  	--input-product-id $JOBSPEC \
  	--output-format gtiff \
  	--include-top-of-atmosphere \
  	--include-brightness-temperature \
  	--include-surface-reflectance \
  	--bridge-mode \
  	--input-url $JOBINPUTURL"
   TOAST=`expr $TOAST + 1`
done) | parallel --max-procs 2 --progress --verbose

export UNIQID=`date +%s`
mkdir -p /efs/testruns/$UNIQID
rsync -av /home/espa/output-data/ /efs/testruns/$UNIQID/
