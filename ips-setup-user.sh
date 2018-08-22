#!/usr/bin/bash -x

# User configuration parameters
#
# Directory where IPS source can be found
SRCDIR=/sno04/development/jcavanaugh/ips-all

# User name and UID
USER_NAME=jcavanaugh

DATA2=/data2

cd $SRCDIR

# Copy in fixed up setup_db script
if [ -f setup_db ]; then
	cp setup_db $DATA2/ias_sys/collection1/setup/setup_db
fi

# Initialize environment variables
. env-rpmbuild.sh

# Set symbolic links to input data
cd $DATA2/ias_sys/collection1/proddata
ln -s /LOSRLPGD03$DATA2/IandT_testdata/ias_rel13.0/rlut/collection1 rlut
ln -s /LOSRLPGD03$DATA2/dem .
cd sysdata/
ln -s /LOSRLPGD03$DATA2/stray_light_vectors/ .

# Fix up NOVAS home directory
cd $DATA2/ias_sys/collection1/setup
sed --in-place -e's/setenv NOVAS_HOME \$COTS\/novas3.1/setenv NOVAS_HOME \/usr\/share\/novas/' iaslib_setup

# Set more environment variables
export TNS_ADMIN=/usr/lib/oracle/12.2/client64/network/admin
export IAS_SERVICE_DIR=/home/ipecm/cpf_ce_PERL/install
export IAS_LOGGING=FILE
mkdir -p $DATA2/ias_sys/collection1/proddata/log
export IAS_LOG=$DATA2/ias_sys/collection1/proddata/log
export COTS=null

# Set up PERL paths
export PERL5LIB=/opt/perllib:/opt/perllib/lib/perl5
export PATH=$PATH:/opt/bin

cd $SRCDIR
./ips/ias_base/setup/setup_dirs.csh
export IAS_SERVICES=http://LOSRLIAT02:9002
rm -rf $DATA2/ias_sys/collection1/proddata/wo
ln -s $SRCDIR/../wotmp $DATA2/ias_sys/collection1/proddata/wo
export IAS_DATA_DIR=/LOSRLPGD03/$DATA2
export PROCESSING_SYSTEM=IAS

ips/create_setup_file.csh ias dev
