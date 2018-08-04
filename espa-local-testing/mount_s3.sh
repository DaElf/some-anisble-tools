#!/bin/sh -x

mkdir -p /s3/auxiliaries/elevation
goofys -o allow_other lsds-mvp-elevation-aux /s3/auxiliaries/elevation
mkdir -p /s3/auxiliaries/aster
goofys -o allow_other lsds-mvp-aster-aux /s3/auxiliaries/aster
mkdir -p /s3/auxiliaries/L47
goofys -o allow_other lsds-mvp-l47-sr-aux /s3/auxiliaries/L47
mkdir -p /s3/auxiliaries/L8
goofys -o allow_other lsds-mvp-l8-sr-aux /s3/auxiliaries/L8
mkdir -p /s3/auxiliaries/NARR
goofys -o allow_other lsds-mvp-narr-aux:/NARR /s3/auxiliaries/NARR
mkdir -p /s3/auxiliaries/MODTRAN-DATA
goofys -o allow_other modtran-data-landsat.io /s3/auxiliaries/MODTRAN-DATA
