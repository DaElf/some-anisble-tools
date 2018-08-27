docker run --rm --tty -it\
  --cap-add=SYS_ADMIN \
  --cap-add=SYS_PTRACE \
  --hostname $USER-ips \
  --name $USER-ips \
  -e DISPLAY=$DISPLAY \
  --ipc=host \
  --volume /devel:/devel:rw \
  --volume /s3:/s3:ro \
  --volume /jobtmp:/jobtmp:rw \
  --volume /tmp/.X11-unix:/tmp/.X11-unix:rw \
  --workdir $(pwd) \
  707566951618.dkr.ecr.us-west-2.amazonaws.com/ips-process/develop \
  bash

  #--cap-add LINUX_IMMUTABLE \
  #-p 11022:22 \
