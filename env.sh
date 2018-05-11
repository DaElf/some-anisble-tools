

sub_dir=build_ias
export DEVDIR=/LOSRLPGD03/development/rcattelan
export SRCROOT=$DEVDIR/ips-all/ips

export CXXFLAGS='-g -Wall -O2 -march=nocona -mfpmath=sse -msse2'
export CFLAGS=$CXXFLAGS
#export QTDIR=/usr/local/qt_12c
export QTDIR=/usr/lib64/qt4
export PERL5LIB=$DEVDIR/$sub_dir/perllib:$DEVDIR/$sub_dir/perllib:$DEVDIR/$sub_dir/perllib/lib/perl5
export PYTHONPATH=$DEVDIR/$sub_dir/python/lib/python3.4/site-packages:$DEVDIR/$sub_dir/pylib
#export JUNIT_HOME=/usr/share/java
# single path -- do not add colon separated paths
export JAVA_LIB=/home/ipecm/ips_COTS64/javalib

export PATH=$QTDIR/bin
export PATH=$PATH:/home/ipecm/ips_COTS64/hdf5/bin
export PATH=$PATH:/home/ipecm/ips_COTS64/hdfview/bin
export PATH=$PATH:/sbin:/bin:/usr/sbin:/usr/bin
export PATH=$PATH:/LOSRLPGD03/development/rcattelan/$sub_dir/bin
export PATH=$PATH:${ORACLE_HOME}/bin

#export PATH=$PATH:/home/ipecm/ips_COTS64/gdal/bin

export LD_LIBRARY_PATH=/usr/lib64
#export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/qt_12c/lib
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${ORACLE_HOME}/lib
#export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/ipecm/ips_COTS64/gdal/lib
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$DEVDIR/$sub_dir/lib

#export PATH=$PATH:/opt/bin
#export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/lib

export ENABLE_DB_TESTS=
export GLS_LIB=/pcache/level1/gls
export TLE_LIB=/pcache/level1/tle

export COTS=/home/ipecm/ips_COTS64

export CUBIST_HOME=/home/ipecm/ips_COTS64/cubist

export CGREENINC=/home/ipecm/ips_COTS64/cgreen/include
export CGREENLIB=/home/ipecm/ips_COTS64/cgreen/lib
export CGREEN_HOME=/home/ipecm/ips_COTS64/cgreen

#export FFTWINC=/home/ipecm/ips_COTS64/fftw/include
#export FFTWLIB=/home/ipecm/ips_COTS64/fftw/lib
#export FFTW_HOME=/home/ipecm/ips_COTS64/fftw

export GCTP2INC=/home/ipecm/ips_COTS64/gctp/include
export GCTP2LIB=/home/ipecm/ips_COTS64/gctp/lib
export GCTP2_HOME=/home/ipecm/ips_COTS64/gctp

export GCTPINC=/home/ipecm/ips_COTS64/gctp3/include
export GCTPLIB=/home/ipecm/ips_COTS64/gctp3/lib
export GCTP_HOME=/home/ipecm/ips_COTS64/gctp3

#export GDAL_HOME=/home/ipecm/ips_COTS64/gdal

export GEOTIFF_HOME=/home/ipecm/ips_COTS64/tiff
export TIFF_HOME=/home/ipecm/ips_COTS64/tiff

export GSL_HOME=/home/ipecm/ips_COTS64/gsl

#export HDF5INC=/home/ipecm/ips_COTS64/hdf5/include
#export HDF5LIB=/home/ipecm/ips_COTS64/hdf5/lib
#export HDF5_HOME=/home/ipecm/ips_COTS64/hdf5

export HDFINC=/home/ipecm/ips_COTS64/hdf/include
export HDFLIB=/home/ipecm/ips_COTS64/hdf/lib
export HDF_HOME=/home/ipecm/ips_COTS64/hdf

export JPLDE421=/home/ipecm/ips_COTS64/novas3.1/data/lnxp1900p2053.421

export MATH_HOME=/home/ipecm/ips_COTS64

export NOVAS_HOME=/home/ipecm/ips_COTS64/novas3.1
export NOVASINC=/home/ipecm/ips_COTS64/novas3.1/include
export NOVASLIB=/home/ipecm/ips_COTS64/novas3.1/lib

export ODBC_HOME=/usr
export ODBC_INC=/usr/include
export ODBC_LIB=/usr/lib64

export ODL_HOME=/home/ipecm/ips_COTS64/odl
export ODLINC=/home/ipecm/ips_COTS64/odl
export ODLLIB=/home/ipecm/ips_COTS64/odl

export REMEZ_HOME=/home/ipecm/ips_COTS64/remez
export REMEZINC=/home/ipecm/ips_COTS64/remez/include
export REMEZLIB=/home/ipecm/ips_COTS64/remez/lib

export SHP_HOME=/home/ipecm/ips_COTS64/shape
export SHPINC=/home/ipecm/ips_COTS64/shape/include
export SHPLIB=/home/ipecm/ips_COTS64/shape/lib

export TNS_ADMIN=/home/rcattelan
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
export IAS_SERVICES=http://rcattelan-cli:8081
export IAS_TEMP=/usr/tmp
export LEVEL1_MODE=IAS

DATA2=/rcattelan-cli/data2
export IAS_UNIT_TEST_DATA_DIR=$DATA2/test_data

export IAS_IT_TEST_DATA_DIR=/home/iasit/testdata
export IAS_SERVICE_DIR=/home/ipecm/cpf_service_PERL/install
export IAS_SYS=$DATA2/rcattelan/ias_sys/collection1
export IAS_OPS=$DATA2/rcattelan/ias_sys/collection1
export IAS_SYS_DIR=$DATA2/rcattelan/ias_sys/collection1

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

