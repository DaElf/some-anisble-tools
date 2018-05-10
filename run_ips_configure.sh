#!/bin/sh -x

(cd ips; [ -e configure ] || ./autogen.sh)
(cd ips; ./configure --enable-ias_qt_lib --prefix=/LOSRLPGD03/development/rcattelan/build_ias )
#(cd ips; ./configure --enable-ias_qt_lib --prefix=/opt )
