docker run --rm --tty -it\
  --cap-add=SYS_ADMIN \
  --hostname $USER-ips \
  --name $USER-ips \
  -e DISPLAY=$DISPLAY \
  --ipc=host \
  --volume /LOSRLPGD03/development:/LOSRLPGD03/development:rw \
  --volume /LOSRLPGD03/data2:/LOSRLPGD03/data2:rw \
  --volume /home/$USER:/home/$USER:rw \
  --volume /tmp/.X11-unix:/tmp/.X11-unix:rw \
  --volume /sno4:/sno4:rw \
  --workdir /LOSRLPGD03/development/$USER \
  707566951618.dkr.ecr.us-west-2.amazonaws.com/ips-process/develop \
  bash

  #--cap-add LINUX_IMMUTABLE \
  #-p 11022:22 \
