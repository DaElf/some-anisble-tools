

DATA2=/data2
export DEVDIR=/opt
export TNS_ADMIN=/home/ips

export SRCROOT=$DEVDIR/ips-all/ips

export CXXFLAGS='-g -Wall -O2 -march=nocona -mfpmath=sse -msse2'
export CFLAGS=$CXXFLAGS
export QTDIR=/usr/lib64/qt4

export PERL5LIB=$DEVDIR/perllib:$DEVDIR/perllib/lib/perl5
export PYTHONPATH=$DEVDIR/python/lib/python3.4/site-packages:$DEVDIR/pylib
#export JUNIT_HOME=/usr/share/java
# single path -- do not add colon separated paths
export JAVA_LIB=$(pwd)/javalib-hack

export PATH=$QTDIR/bin
export PATH=$PATH:/sbin:/bin:/usr/sbin:/usr/bin
export PATH=$PATH:${ORACLE_HOME}/bin
export PATH=$PATH:${DEVDIR}/bin

export LD_LIBRARY_PATH=/usr/lib64
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$DEVDIR/lib

export ENABLE_DB_TESTS=
export GLS_LIB=/pcache/level1/gls
export TLE_LIB=/pcache/level1/tle


export JPLDE421=/usr/share/novas/data/lnxp1900p2053.421

export ODBC_HOME=/usr
export ODBC_INC=/usr/include
export ODBC_LIB=/usr/lib64

export ORACLE_HOME=/usr/lib/oracle/12.2/client64
export ORACLE_SID=ORCL
export TWO_TASK=ORCL
export IAS_DB_COM=ias_ops/cloud123
export IAS_DB_L8_OLITIRS=l8_ias/cloud123
export IAS_DB_L8_OLITIRS_EVAL=l8_ias_eval/cloud123
export IAS_DB_L7_ETM=etmops/cloud123
export IAS_DB_L5_TM=tmops/cloud123
export IAS_DB_L4_TM=l4tmops/cloud123
export IAS_DB_L5_MSS=l5mssops/cloud123
export IAS_DB_L4_MSS=l4mssops/cloud123
export IAS_DB_L3_MSS=l3mssops/cloud123
export IAS_DB_L2_MSS=l2mssops/cloud123
export IAS_DB_L1_MSS=l1mssops/cloud123

export IAS_BUILD_64BIT=1
export IASBASE_PERLLIB=$DEVDIR/perllib
export IASBASE_PYLIB=$DEVDIR/pylib
export IASBUILD=$DEVDIR
export IASLIB_BASE=$DEVDIR
export IASLIB_INC=$DEVDIR/include
export IASLIB_LIB=$DEVDIR/lib
export IASLIB_PERLLIB=$DEVDIR/perllib
export IASLIB_PYLIB=$DEVDIR/python
export IAS_INC=$DEVDIR/include
export IAS_LIB=$DEVDIR/lib
export IAS_BIN=$DEVDIR/bin
export IAS_JAVA_LIB=$DEVDIR/javalib

export IAS_SYSTEM_USER_ID=jcavanaugh
export IAS_SYSTEM_ID=I
export IAS_DEVELOPMENT_ENV=yes
export IAS_INSTANCE_NAME=Collection1
export IAS_TEMP=/usr/tmp
export LEVEL1_MODE=IAS

export IAS_IT_TEST_DATA_DIR=/home/iasit/testdata

export IAS_UNIT_TEST_DATA_DIR=$DATA2/test_data
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

export IAS_IMG=$IAS_OPS/proddata/sysdata/image
export IAS_LOG=$IAS_OPS/proddata/log
export IAS_RPS=$IAS_OPS/share/rps
export IAS_RPSDATA=$IAS_OPS/share/rps
export IAS_SCRT=$IAS_OPS/proddata/temp/test_script
export IAS_TAR=$IAS_OPS/proddata/temp/tar
export IAS_TEMPLATE_DIR=$IAS_OPS/share/templates
export IAS_WO=$IAS_OPS/proddata/wo
export ICEM_CONFIGFILE_NAME=$IAS_OPS/share/rps/rxx_ICEMConfig.odl
export ICRE_CONFIGFILE_NAME=$IAS_OPS/share/rps/rxx_ICREConfig.odl
export LEAP_SECONDS_FILE=$IAS_OPS/proddata/sysdata/leap_seconds.odl
export CPF_REPOSITORY_DIR=$IAS_OPS/proddata/product
export CRAMCONFIG=$IAS_OPS/proddata/rps/rcr_CRaMconfig.odl
export CRAMDB_DIR=$IAS_OPS/share/CRAMdb
export GLS_DEM=$IAS_OPS/proddata/dem/gls

export PROCESSING_CENTER=EROS
export PROCESSING_SYSTEM=IAS_LCDM
