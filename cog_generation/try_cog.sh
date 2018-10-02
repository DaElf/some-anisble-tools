#!/bin/sh
#set -x
set -e

#without=$(basename $file)
#base="${without%.*}"
file=$1
mkdir -p cog
rm -f $file.ovr

gdaladdo \
    --config PREDICTOR_OVERVIEW 2 \
    --config GDAL_TIFF_OVR_BLOCKSIZE 512 \
    -q -ro -r average \
    $file \
    2 4 8 16 32

gdal_translate \
    -co TILED=YES \
    -co COMPRESS=DEFLATE \
    $file.ovr cog/$file.ovr

gdal_translate \
    -co TILED=YES \
    -co COMPRESS=DEFLATE \
    -co COPY_SRC_OVERVIEWS=YES \
    -co BLOCKXSIZE=512 \
    -co BLOCKYSIZE=512 \
    --config GDAL_TIFF_OVR_BLOCKSIZE 512 \
    $file cog/$file
