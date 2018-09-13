#!/bin/sh

dir=$(dirname "$0")
. $dir/env-aws.sh

my_dir=$(mktemp -p /jobtmp -d -t ips_worker.XXXXXX) || exit 1
chmod 777 $my_dir
log=/jobtmp/log
mkdir -p $log
export IAS_LOG=$log
env

mkdir -p $my_dir/LC80170392013141LGN03
aws s3 cp s3://dev-lsds-l8-test-l0rp/LC80170392013141LGN03.tar.gz - | tar --use-compress-program=pigz -xvf - -C $my_dir/LC80170392013141LGN03

string=$(/opt/bin/PWG \
    -parm DSW:CAL_PARM_FILENAME=/s3/auxiliaries/landsat/cpf/LC08CPF_20130401_20130627_02.01 \
    -parm DSW:BIAS_PARM_FILENAME_OLI=/s3/auxiliaries/landsat/bpf/LO8BPF20130319181117_20130319182238.01 \
    -parm DSW:BIAS_PARM_FILENAME_TIRS=/s3/auxiliaries/landsat/bpf/LT8BPF20130411170539_20130411172812.01 \
    -parm DSW:RLUT_FILENAME=/s3/auxiliaries/landsat/rlut/LC08RLUT_20130211_20150302_01_11.h5 \
    -parm DFP:L1G_PACKAGE=1 \
    -parm DFP:NAME_USING_PRODUCT_ID=1 \
    -script DSC:SKIP \
    -scene LC80170392013141LGN03  \
    -procedure "L1T with Quality Band" \
    -l0r_data_path $my_dir/LC80170392013141LGN03/ \
    -i)

#    -parm  DSW:CREATE_RADIOMETRIC_CHAR_FLAG=0

job=$(echo $string | awk -F',|( +)' '{print $11}')
/bin/time -o $my_dir/run_time -v /devel/daelf/ips-all/ips/ias_base/pcs/PWC $job
ret=$?
cat /jobtmp/$job/save/$job.log

cat $my_dir/run_time
echo "Exit now" $ret
exit $ret
