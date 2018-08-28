docker run --rm --tty -it\
  --cap-add LINUX_IMMUTABLE \
  --hostname $USER-cli \
  --name $USER-cli \
  -e DISPLAY=$DISPLAY \
  -p 19022:22 \
  --ipc=host \
  --volume /LOSRLPGD03/development:/LOSRLPGD03/development:rw \
  --volume /LOSRLPGD03/data2:/LOSRLPGD03/data2:rw \
  --volume /home/ipecm:/home/ipecm:ro \
  --volume /home/rcattelan:/home/rcattelan:rw \
  --volume /usr/local/qt_12c:/usr/local/qt_12c:ro \
  --volume /usr/local/Trolltech:/usr/local/Trolltech:ro \
  --volume /tmp/.X11-unix:/tmp/.X11-unix:rw \
  --workdir /home/espa \
  epsa/ips-build bash

#  --volume /home/oracle/12.1.0:/home/oracle/12.1.0:ro \
