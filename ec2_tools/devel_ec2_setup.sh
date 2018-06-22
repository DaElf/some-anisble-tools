#!/bin/sh
set -e
set -x
#yum clean metadata
yum update -y
yum install -y amazon-efs-utils zsh docker
yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm || true

systemctl enable docker
systemctl start docker
systemctl enable nfs
systemctl start nfs

mkdir -p /efs
mkdir -p /devel
[[ $(findmnt -M /devel) ]] ||  mount -t efs fs-15a9c8bc:/ /devel
[[ $(findmnt -M /efs) ]] ||  mount -t efs fs-174024be:/ /efs

rm -f /etc/yum.repos.d/local.repo
cat << 'EOF' > /etc/yum.repos.d/local.repo
[local]
name=CentOS-$releasever - local packages for $basearch
baseurl=file:///efs/CentOS/7/local/$basearch
enabled=1
gpgcheck=0
protect=1
EOF

yum install -y espa-processing

groupadd --gid 7001 cattelan || true
useradd --home-dir /efs/cattelan --shell /bin/zsh --uid 7001 --gid 7001 -G wheel -G docker --password $(openssl passwd -1 cattelan) cattelan || true
