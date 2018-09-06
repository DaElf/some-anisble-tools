#!/bin/sh

. ./setup_db-aws

MODE=LPGS
DATA2=
PREFIX=/opt
export TNS_ADMIN=/home/ips

export IAS_WO=/jobtmp
export QTDIR=/usr/lib64/qt4

export PERL5LIB=$PREFIX/perllib:$PREFIX/perllib/lib/perl5
export PYTHONPATH=$PREFIX/lib/python3.4/site-packages:$PREFIX/pylib
# single path -- do not add colon separated paths
export JAVA_LIB=$(pwd)/javalib-hack

export PATH=$QTDIR/bin:/sbin:/bin:/usr/sbin:/usr/bin:${ORACLE_HOME}/bin:$PREFIX/bin

export LD_LIBRARY_PATH=:$PREFIX/lib
export IAS_BIN=$PREFIX/bin

export ENABLE_DB_TESTS=
export GLS_LIB=/pcache/level1/gls
export TLE_LIB=/pcache/level1/tle

export IAS_SERVICES=http://sillyrabbit

export JPLDE421=/usr/share/novas/data/lnxp1900p2053.421

export ORACLE_HOME=/usr/lib/oracle/12.2/client64

export IAS_BUILD_64BIT=1
export IASBASE_PERLLIB=$PREFIX/perllib
export IASBASE_PYLIB=$PREFIX/pylib
export IASLIB_BASE=$PREFIX
export IASLIB_PERLLIB=$PREFIX/perllib
export IASLIB_PYLIB=$PREFIX/python
export IAS_JAVA_LIB=$PREFIX/javalib

export IAS_SYSTEM_USER_ID=$USER
export IAS_DEVELOPMENT_ENV=yes
export IAS_INSTANCE_NAME=Collection1
export IAS_TEMP=/usr/tmp

if [ $MODE == "LPGS" ]; then
  export LEVEL1_MODE=LPGS
  export L1_SYSTEM_ID=L
  export IAS_SYSTEM_ID=L
  export PROCESSING_SYSTEM=LPGS
else
  export LEVEL1_MODE=IAS
  export L1_SYSTEM_ID=I
  export IAS_SYSTEM_ID=I
  export PROCESSING_SYSTEM=IAS
fi
export IAS_IT_TEST_DATA_DIR=/home/iasit/testdata

#export IAS_UNIT_TEST_DATA_DIR=$DATA2/test_data
export IAS_SYS=$DATA2/ias_sys/collection1
export IAS_OPS=$DATA2/ias_sys/collection1
export IAS_SYS_DIR=$DATA2/ias_sys/collection1

export IASTOOLS=$IAS_OPS/share/tools
export IAS_CSR=$IAS_OPS/proddata/product/csr
export IAS_DATA_DIR=$IAS_OPS/proddata
export IASCPF_LIB=$IAS_OPS/proddata/product/cpf
export IASDEM=$IAS_OPS/proddata/dem
export IASGCP=$IAS_OPS/proddata/sysdata/gcp
export IASIMAGES=$IAS_OPS/proddata/sysdata/l17_image

export IAS_LOGGING=FILE
export IAS_IMG=$IAS_OPS/proddata/sysdata/image
export IAS_LOG=$IAS_OPS/proddata/log
export IAS_RPS=$IAS_OPS/share/rps
export IAS_RPSDATA=$IAS_OPS/share/rps
export IAS_SCRT=$IAS_OPS/proddata/temp/test_script
export IAS_TAR=$IAS_OPS/proddata/temp/tar
export IAS_TEMPLATE_DIR=$IAS_OPS/share/templates
export ICEM_CONFIGFILE_NAME=$IAS_OPS/share/rps/rxx_ICEMConfig.odl
export ICRE_CONFIGFILE_NAME=$IAS_OPS/share/rps/rxx_ICREConfig.odl
export LEAP_SECONDS_FILE=$IAS_OPS/proddata/sysdata/leap_seconds.odl
export CPF_REPOSITORY_DIR=$IAS_OPS/proddata/product
export CRAMCONFIG=$IAS_OPS/proddata/rps/rcr_CRaMconfig.odl
export CRAMDB_DIR=$IAS_OPS/share/CRAMdb
export GLS_DEM=$IAS_OPS/proddata/dem/gls

export PROCESSING_CENTER=EROS
