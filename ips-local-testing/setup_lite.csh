#!/usr/bin/env tcsh -x
setenv DEVDIR /LOSRLPGD03/development/rcattelan

#setenv ORACLE_HOME /usr/lib/oracle/12.2/client64
setenv ORACLE_HOME  /home/oracle/12.1.0

setenv SRCROOT $DEVDIR/ips-all/ips
setenv JAVA_LIB /home/ipecm/ips_COTS64/javalib

setenv LD_LIBRARY_PATH /usr/lib64

#setenv QTDIR /usr/lib64/qt4

set instance = "Collection1"
set lc_instance = `echo $instance | tr "[:upper:]" "[:lower:]"`
source $SRCROOT/ias_lib/setup/setup_db olidev rcattelan rcattelan123
source $SRCROOT/ias_lib/setup/iaslib_setup --enable-dev --64 $DEVDIR/build_ias
#source $SRCROOT/ias_base/setup/iasbase_setup /$HOST/development/$USER-data/ias_sys/$lc_instance $instance
source $SRCROOT/ias_base/setup/iasbase_setup /$HOST/data2/$USER/ias_sys/$lc_instance $instance
source $SRCROOT/ias/setup_l17/ias17_setup
source $SRCROOT/ias/setup/ias_setup

