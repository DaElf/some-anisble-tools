#!/bin/sh -x

#sudo mkdir -p /media/ephemeral0
#sudo chmod 777 /media/ephemeral0
sudo chmod 777 /jobtmp
my_dir=$(dirname "$0")
cd $my_dir

sudo -u espa -s <<EOF
set -x
pwd

gpg --import ./gpg-tools/USGS_private.gpg || true

export AWS_DEFAULT_REGION=us-west-2
export PYTHONPATH=/devel/daelf/espa-all/espa-processing/processing

time /devel/daelf/espa-all/espa-processing/processing/espa_batch_worker.py $1

EOF

ret=$?
echo "Exit now" $ret
exit $ret
