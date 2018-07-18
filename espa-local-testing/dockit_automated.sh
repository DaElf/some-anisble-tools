#!/bin/sh
#set -x
set -e

host_addr=$(ip -4 a show docker0 | grep inet | awk  'BEGIN {FS = "[ /]+" } {print $3}')

sudo mkdir -p /jobtmp
sudo chmod 777 /jobtmp

docker run --rm -it \
  --user espa \
  --add-host=docker.local:$host_addr \
  --cap-add LINUX_IMMUTABLE \
  --cap-add SYS_PTRACE \
  --hostname $USER-espa \
  --name $USER-espa-$$ \
  --volume /s3:/s3:ro \
  --volume /devel:/devel:rw \
  --volume /jobtmp:/jobtmp:rw \
  --workdir $(pwd) \
  707566951618.dkr.ecr.us-west-2.amazonaws.com/espa-process/devel:latest \
  $(pwd)/espa-worker.sh