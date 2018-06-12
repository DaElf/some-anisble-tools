#!/bin/sh
#set -x
set -e

host_addr=$(ip -4 a show docker0 | grep inet | awk  'BEGIN {FS = "[ /]+" } {print $3}')

sudo mkdir -p /jobtmp
sudo chmod 777 /jobtmp

docker run --rm \
  --user espa \
  --add-host=docker.local:$host_addr \
  --cap-add LINUX_IMMUTABLE \
  --cap-add SYS_PTRACE \
  --hostname $USER-espa \
  --name $USER-espa-$$ \
  --volume /efs:/efs:rw \
  --volume /devel:/devel:rw \
  --volume /jobtmp:/jobtmp:rw \
  --workdir /efs/espa-container-tools \
  707566951618.dkr.ecr.us-west-2.amazonaws.com/espa-process/devel:latest \
  /efs/espa-container-tools/espa-worker.sh
