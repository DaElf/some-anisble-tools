#!/bin/sh -x

TOAST=0
export JOBLIST=./joblist.txt

for JOBSPEC in `cat $JOBLIST`
do
  #echo $JOBSPEC
  #echo $JOBLONG
  
  # Append JOBSPEC with the filename
  JOBLONG=$JOBSPEC".tar.gz"
  JOBINPUTURL="file:///efs/input/L8/"$JOBLONG
  time cli.py --order-id toast$TOAST \
  	--product-type landsat \
  	--input-product-id $JOBSPEC \
  	--output-format gtiff \
  	--include-top-of-atmosphere \
  	--include-brightness-temperature \
  	--include-surface-reflectance \
  	--bridge-mode \
  	--input-url $JOBINPUTURL &
   TOAST=`expr $TOAST + 1`
done
wait
