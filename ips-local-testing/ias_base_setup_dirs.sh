#!/bin/sh

set -x
set -e

mode=dev  # default to development

install -d -m 775 $IAS_DATA_DIR/wo
install -d -m 775 $IAS_DATA_DIR/log
# install -d -m 775 $IAS_DATA_DIR/l1rg

# The location for RLUT on the processing cache is supposed to be mounted at 
# /pcache/rlut.  If that's not available (e.g., on the development machine), try
# to use an alternate local directory.
if [ -e /pcache/$mode/rlut -a -r /pcache/$mode/rlut ]; then
    ln -fs /pcache/$mode/rlut $IAS_DATA_DIR
elif [ -e /$HOST/data2/rlut_cache ]; then
    rm -f $IAS_DATA_DIR/rlut
    ln -fs /$HOST/data2/rlut_cache $IAS_DATA_DIR/rlut
fi

# The location for DEM on the processing cache is supposed to be mounted at 
# /pcache/dem.  If that's not available (e.g., on the development machine), try
# to use an alternate local directory.
if [ -e /pcache/$mode/dem -a -r /pcache/$mode/dem ]; then
    ln -fs /pcache/$mode/dem $IAS_DATA_DIR
elif [ -e /$HOST/data2/dem ]; then
    ln -fs /$HOST/data2/dem $IAS_DATA_DIR
fi

# Make the directory for reference images (DOQs) on local disk
#  On the dev server just link to the existing files
if  [ -e /$HOST/data2/doq ]; then
    install -d -m 775 $IAS_DATA_DIR/sysdata
    ln -T -f -s /$HOST/data2/doq $IAS_DATA_DIR/sysdata/image
else
    install -d -m 775 $IAS_DATA_DIR/sysdata/image
fi

# Set up the water mask directory for developers
if [ -e /$HOST/data2/water_mask ]; then
    ln -fs /$HOST/data2/water_mask $IAS_DATA_DIR/sysdata
fi

# Set up the TIRS stray light vector directory for developers
if [ -e /$HOST/data2/stray_light_vectors ]; then
    ln -f -s /$HOST/data2/stray_light_vectors $IAS_DATA_DIR/sysdata
fi

install -d -m 775 $IAS_DATA_DIR/temp/tar

install -d -m 775 $IAS_SYS_DIR/share/rps
install -d -m 775 $IAS_SYS_DIR/share/sys
install -d -m 775 $IAS_SYS_DIR/share/tools
install -d -m 775 $IAS_SYS_DIR/test_script
