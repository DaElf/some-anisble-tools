docker run --rm --tty -it\
  --cap-add=SYS_ADMIN \
  --hostname $USER-ips \
  --name $USER-ips \
  -e DISPLAY=$DISPLAY \
  --ipc=host \
  --volume /devel:/devel:rw \
  --volume /s3:/s3:rw \
  --volume /s3/auxiliaries/landsat:/s3/auxiliaries/landsat:ro \
  --volume /s3/auxiliaries/dem:/s3/auxiliaries/dem:ro \
  --volume /s3/l0rp:/s3/l0rp:ro \
  --volume /tmp/.X11-unix:/tmp/.X11-unix:rw \
  --workdir /devel/$USER \
  707566951618.dkr.ecr.us-west-2.amazonaws.com/ips-process/develop \
  bash

  #--cap-add LINUX_IMMUTABLE \
  #-p 11022:22 \
