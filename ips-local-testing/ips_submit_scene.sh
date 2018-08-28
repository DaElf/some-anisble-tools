#!/bin/sh -x

/opt/bin/PWG \
    -scene LC80170392013141LGN03  \
    -procedure "L1T with Quality Band" \
    -l0r_data_path /s3/l0rp/LC80170392013141LGN03/ \
    -parm DSW:CAL_PARM_FILENAME=/s3/auxiliaries/landsat/cpf/LC08CPF_20130401_20130627_02.01 \
    -parm DSW:BIAS_PARM_FILENAME_OLI=/s3/auxiliaries/landsat/bpf/LO8BPF20130319181117_20130319182238.01 \
    -parm DSW:BIAS_PARM_FILENAME_TIRS=/s3/auxiliaries/landsat/bpf/LT8BPF20130411170539_20130411172812.01 \
    -parm DSW:RLUT_FILENAME=/s3/auxiliaries/landsat/rlut/LC08RLUT_20130211_20150302_01_11.h5 \
    -parm DFP:L1G_PACKAGE=1 \
    -parm DFP:NAME_USING_PRODUCT_ID=1
