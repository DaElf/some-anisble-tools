#!/bin/sh -x
set -x

DATA2=/data2
IPS_HOME=/home/ips

# Copy in fixed up setup_db script
#if [ -f setup_db-aws ]; then
#	cp setup_db-aws $DATA2/ias_sys/collection1/setup/setup_db
#fi

# Initialize environment variables
. ./setup_db-aws
. ./env-aws.sh

sudo chown -R ips $IAS_DATA_DIR
# Set symbolic links to input data
(cd $IAS_DATA_DIR; \
 ln -sf /s3/auxiliaries/landsat/rlut . ; \
 ln -sf /s3/auxiliaries/dem . \
)

(cd  $IAS_DATA_DIR/sysdata; \
 ln -sf /s3/auxiliaries/landsat/stray_light_vectors . ;\
 ln -sf /s3/auxiliaries/landsat/water_mask . \
)

# Set more environment variables
install -d -m 775 $IAS_DATA_DIR/log
install -d -m 775 $IAS_DATA_DIR/temp/tar
#install -d -m 775 $IAS_SYS_DIR/share/rps
#install -d -m 775 $IAS_SYS_DIR/share/sys
#install -d -m 775 $IAS_SYS_DIR/share/tools
sudo install -d -m 775 $IAS_SYS_DIR/test_script

