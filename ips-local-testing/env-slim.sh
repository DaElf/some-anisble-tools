

DATA2=/LOSRLPGD03/data2/rcattelan
sub_dir=build_ias
export DEVDIR=/LOSRLPGD03/development/rcattelan
export TNS_ADMIN=/home/rcattelan

export SRCROOT=$DEVDIR/ips-all/ips

export IAS_SERVICES=http://hotdog:8081

export CXXFLAGS='-g -Wall -O2 -march=nocona -mfpmath=sse -msse2'
export CFLAGS=$CXXFLAGS
export QTDIR=/usr/lib64/qt4

export PERL5LIB=$DEVDIR/$sub_dir/perllib:$DEVDIR/$sub_dir/perllib:$DEVDIR/$sub_dir/perllib/lib/perl5
export PYTHONPATH=$DEVDIR/$sub_dir/python/lib/python3.4/site-packages:$DEVDIR/$sub_dir/pylib
#export JUNIT_HOME=/usr/share/java
# single path -- do not add colon separated paths
export JAVA_LIB=$(pwd)/javalib-hack

export PATH=$QTDIR/bin
export PATH=$PATH:/sbin:/bin:/usr/sbin:/usr/bin
export PATH=$PATH:${ORACLE_HOME}/bin

export PATH=$PATH:$DEVDIR/$sub_dir/bin

export LD_LIBRARY_PATH=/usr/lib64
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$DEVDIR/$sub_dir/lib

export ENABLE_DB_TESTS=
export GLS_LIB=/pcache/level1/gls
export TLE_LIB=/pcache/level1/tle

# Fix the code but for now set here
export GEOTIFF_INCLUDES='-I/usr/include/libgeotiff'

export HDF_INCLUDES=-I/usr/include/hdf
export HDF_LDFLAGS=-L/usr/lib64/hdf
export HDFINC=/usr/include/hdf
export HDFLIB=/usr/lib64/hdf

export JPLDE421=/usr/share/novas/data/lnxp1900p2053.421

export ODBC_HOME=/usr
export ODBC_INC=/usr/include
export ODBC_LIB=/usr/lib64

export ORACLE_HOME=/usr/lib/oracle/12.2/client64
export ORACLE_SID=crdev
export TWO_TASK=crdev
export IAS_OUI_DB=rcattelan_wo_common/rcattelan123
export IAS_DB_COM=rcattelan_wo_common/rcattelan123
export IAS_DB_L1_MSS=rcattelan_l1_mss/rcattelan123
export IAS_DB_L2_MSS=rcattelan_l2_mss/rcattelan123
export IAS_DB_L3_MSS=rcattelan_l3_mss/rcattelan123
export IAS_DB_L4_MSS=rcattelan_l4_mss/rcattelan123
export IAS_DB_L4_TM=rcattelan_l4_tm/rcattelan123
export IAS_DB_L5_MSS=rcattelan_l5_mss/rcattelan123
export IAS_DB_L5_TM=rcattelan_l5_tm/rcattelan123
export IAS_DB_L7_ETM=rcattelan_l7_etm/rcattelan123
export IAS_DB_L8_OLITIRS=rcattelan_l8/rcattelan123
export IAS_DB_L8_OLITIRS_EVAL=rcattelan_l8/rcattelan123
export IAS_DB_TRAM=rcattelan_tram/rcattelan123

export IAS_BUILD_64BIT=1
export IASBASE_PERLLIB=$DEVDIR/$sub_dir/perllib
export IASBASE_PYLIB=$DEVDIR/$sub_dir/pylib
export IASBUILD=$DEVDIR/$sub_dir
export IASLIB_BASE=$DEVDIR/$sub_dir
export IASLIB_INC=$DEVDIR/$sub_dir/include
export IASLIB_LIB=$DEVDIR/$sub_dir/lib
export IASLIB_PERLLIB=$DEVDIR/$sub_dir/perllib
export IASLIB_PYLIB=$DEVDIR/$sub_dir/python
export IAS_INC=$DEVDIR/$sub_dir/include
export IAS_LIB=$DEVDIR/$sub_dir/lib
export IAS_BIN=$DEVDIR/$sub_dir/bin
export IAS_JAVA_LIB=$DEVDIR/$sub_dir/javalib

export IAS_SYSTEM_USER_ID=rcattelan
export IAS_SYSTEM_ID=I
export IAS_DEVELOPMENT_ENV=yes
export IAS_INSTANCE_NAME=Collection1
export IAS_TEMP=/usr/tmp
export LEVEL1_MODE=IAS

export IAS_IT_TEST_DATA_DIR=/home/iasit/testdata
export IAS_SERVICE_DIR=/home/ipecm/cpf_service_PERL/install

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
export PROCESSING_SYSTEM=IAS
