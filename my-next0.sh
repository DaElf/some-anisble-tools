#!/bin/sh -x

docker run --rm --tty -it\
  --cap-add=SYS_ADMIN \
  --hostname $USER-next0 \
  --name $USER-next0 \
  -e DISPLAY=$DISPLAY \
  -p 11022:22 \
  --ipc=host \
  --volume /Users/cattelan:/Users/cattelan:rw \
  --volume /tmp/.X11-unix:/tmp/.X11-unix:rw \
  --workdir /home/espa \
  epsa/ips-next0 bash

  #--cap-add LINUX_IMMUTABLE \
