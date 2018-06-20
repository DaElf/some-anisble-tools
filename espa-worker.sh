#!/bin/sh -x

pushd /efs/auxiliaries/aster
python -m SimpleHTTPServer 1666 &
pid=$!; echo "simple server pid $pid"
popd

gpg --import USGS_private.gpg || true

espa-worker

kill $pid
