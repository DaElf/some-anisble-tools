#!/bin/sh -x

host_addr=$(ip -4 a show docker0 | grep inet | awk  'BEGIN {FS = "[ /]+" } {print $3}')

docker run --rm --tty -it \
  -p 19022:22 \
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
  bash

