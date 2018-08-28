# Set up the environment variables
setenv DEBUGGER /usr/bin/gdb


# alias to setup the environment for a worktree
alias wkenv 'setipsenv $DEVDIR/dev/\!:1 Collection1'
alias wklpgsenv 'setipslpgsenv $DEVDIR/dev/\!:1 Collection1'

setenv DEVDIR /LOSRLPGD03/development/rcattelan
alias devdir 'cd /LOSRLPGD03/development/rcattelan/\!*'
#alias datadir 'cd /LOSRLPGD03/data1/rcattelan'
alias data2dir 'cd /LOSRLPGD03/development/rcattelan-data'
alias libdir 'cd $SRCROOT/ias_lib/\!*'
alias basedir 'cd $SRCROOT/ias_base/\!*'
alias iasdir 'cd $SRCROOT/ias/\!*'
alias lpgsdir 'cd $SRCROOT/lpgs/\!*'

alias dbdir 'cd $SRCROOT/../ips_database'
alias iasdbdir 'cd $SRCROOT/../ips_database/DATABASE/SUBSYSTEM/IAS'
alias lpgsdbdir 'cd $SRCROOT/../ips_database/DATABASE/SUBSYSTEM/LPGS'


# Create a generic alias for setting up an IAS environment. It takes an
# # optional second parameter to set a custom instance name.
# #        if ($instance == "") set instance = "Collection1"; \\

alias setiasenv 'setenv BUILDROOT \!:1; \\
        set instance = `echo \!:2* | awk '"'"'{ print $1 } '"'"'`; \\
        setenv SRCROOT $BUILDROOT/oli_ias; \\
        if ($instance == "") set instance = "Collection1"; \\
        set lc_instance = `echo $instance | tr "[:upper:]" "[:lower:]"`; \\
        source $SRCROOT/ias_lib/setup/setup_db olidev rcattelan rcattelan123; \\
        source $SRCROOT/ias_lib/setup/iaslib_setup --enable-dev --64 $BUILDROOT/build_ias; \\
        source $SRCROOT/ias_base/setup/iasbase_setup /$HOST/development/$USER-data/ias_sys/$lc_instance $instance; \\
        source $SRCROOT/ias/setup/ias_setup;'

alias setipsenv 'setenv BUILDROOT \!:1; \\
        set instance = `echo \!:2* | awk '"'"'{ print $1 } '"'"'`; \\
        setenv SRCROOT $BUILDROOT/ips; \\
        if ($instance == "") set instance = "Collection1"; \\
        set lc_instance = `echo $instance | tr "[:upper:]" "[:lower:]"`; \\
        source $SRCROOT/ias_lib/setup/setup_db olidev rcattelan rcattelan123; \\
        source $SRCROOT/ias_lib/setup/iaslib_setup --enable-dev --64 $BUILDROOT/build_ias; \\
        source $SRCROOT/ias_base/setup/iasbase_setup /$HOST/development/$USER-data/ias_sys/$lc_instance $instance; \\
        source $SRCROOT/ias/setup_l17/ias17_setup; \\
        source $SRCROOT/ias/setup/ias_setup;'


# Create a generic alias for setting up an LPGS environment.  It takes an
# # optional second parameter to set a custom instance name.
alias setlpgsenv 'setenv BUILDROOT \!:1; \\
        set instance = `echo \!:2* | awk '"'"'{ print $1 } '"'"'`; \\
        set lc_instance = `echo $instance | tr "[:upper:]" "[:lower:]"`; \\
        setenv SRCROOT $BUILDROOT/oli_ias; \\
        source $SRCROOT/ias_lib/setup/setup_db lpgsdev rcattelan rcattelan123; \\
        source $SRCROOT/ias_lib/setup/iaslib_setup --enable-dev --64 $BUILDROOT/build_ias; \\
        source $SRCROOT/ias_base/setup/iasbase_setup /pcachedev/lpgs/${USER}/$lc_instance $instance; \\
        source $SRCROOT/lpgs/setup/lpgs_setup;'

alias setipslpgsenv 'setenv BUILDROOT \!:1; \\
        set instance = `echo \!:2* | awk '"'"'{ print $1 } '"'"'`; \\
        if ($instance == "") set instance = "Collection1"; \\
        set lc_instance = `echo $instance | tr "[:upper:]" "[:lower:]"`; \\
        setenv SRCROOT $BUILDROOT/ips; \\
        source $SRCROOT/ias_lib/setup/setup_db lpgsdev rcattelan rcattelan123; \\
        source $SRCROOT/ias_lib/setup/iaslib_setup --enable-dev --64 $BUILDROOT/build_ias; \\
        source $SRCROOT/ias_base/setup/iasbase_setup /pcachedev/lpgs/${USER}/$lc_instance $instance; \\
        source $SRCROOT/lpgs/setup/lpgs_setup; \\
        setenv IAS_LOGGING FILE;'


