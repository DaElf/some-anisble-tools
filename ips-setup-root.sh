#!/usr/bin/bash -x

# User configuration parameters
#
# Directory where IPS source can be found
SRCDIR=/sno04/development/jcavanaugh/ips-all

# User name and UID
USER_NAME=jcavanaugh
USER_ID=16345		# Same as on Corndog

DATA2=/data2

# Set up user
useradd $USER_NAME -u $USER_ID --no-create-home
usermod -aG ipe $USER_NAME

# Set up Oracle files
mkdir -p /usr/lib/oracle/12.2/client64/network/admin
cd /usr/lib/oracle/12.2/client64/network/admin
cp $SRCDIR/tnsnames.ora .
ln -s /etc/odbcinst.ini odbcinst.ini
ln -s /home/$USER_NAME/.odbc.ini odbc.ini

# Take ownership of data directory
chown -R $USER_NAME $DATA2
