#!/bin/sh -x
mkdir -p /home/espa/.usgs/espa
chown -R espa /home/espa/.usgs/espa
mkdir -p /jobtmp
sudo chown espa /jobtmp
sudo /usr/sbin/sshd-keygen
sudo /usr/sbin/sshd &
cp /efs/DEMO/processing.conf /home/espa/.usgs/espa/processing.conf
