#!/bin/sh -x

host_addr=$(ip -4 a show docker0 | grep inet | awk  'BEGIN {FS = "[ /]+" } {print $3}')

docker run --rm --tty -it\
  --add-host=docker.local:$host_addr \
  --cap-add LINUX_IMMUTABLE \
  --cap-add SYS_PTRACE \
  --hostname $USER-espa \
  --name $USER-espa-$$ \
  --volume /efs:/efs:rw \
  --volume /jobtmp:/jobtmp:rw \
  --workdir /home/espa \
  707566951618.dkr.ecr.us-west-2.amazonaws.com/espa-daelf/processing:latest \
  bash

