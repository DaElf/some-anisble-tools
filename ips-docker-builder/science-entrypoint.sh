#!/bin/bash
set -e

# Add the espa runtime installation directory to the path
export PATH=$PREFIX/bin:$PATH

# Set these because they are not set automatically
#export USER=espa
#export HOME=/home/espa

# Don't create *.pyc files
#export PYTHONDONTWRITEBYTECODE=1

# Now execute the requested application
exec $@
