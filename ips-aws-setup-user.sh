#!/usr/bin/bash -x

# User configuration parameters
#

DATA2=/data2

# Copy in fixed up setup_db script
if [ -f setup_db-aws ]; then
	cp setup_db-aws $DATA2/ias_sys/collection1/setup/setup_db
fi

# Initialize environment variables
. env-aws.sh

# Set symbolic links to input data
(cd $DATA2/ias_sys/collection1/proddata; \
ln -s /s3/auxiliaries/landsat/rlut/ rlut; \
ln -s /s3/auxiliaries/dem .; \
cd sysdata; \
ln -s /s3/auxiliaries/stray_light_vectors/ .)

# Fix up NOVAS home directory
(cd $DATA2/ias_sys/collection1/setup \
sed --in-place -e's/setenv NOVAS_HOME \$COTS\/novas3.1/setenv NOVAS_HOME \/usr\/share\/novas/' iaslib_setup)

# Set more environment variables
export IAS_LOGGING=FILE
mkdir -p $DATA2/ias_sys/collection1/proddata/log
export IAS_LOG=$DATA2/ias_sys/collection1/proddata/log
export COTS=null

# Set up PERL paths
export PERL5LIB=/opt/perllib:/opt/perllib/lib/perl5

./ips/ias_base/setup/setup_dirs.csh
export IAS_WO=/jobtmp
export PROCESSING_SYSTEM=IAS

ips/create_setup_file.csh ias dev
