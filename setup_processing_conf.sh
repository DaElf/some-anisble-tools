#!/bin/sh -x
mkdir -p /home/espa/.usgs/espa
chown -R espa /home/espa/.usgs/espa
mkdir -p /jobtmp
cp /efs/DEMO/processing.conf /home/espa/.usgs/espa/processing.conf
