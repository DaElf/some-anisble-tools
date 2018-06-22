#!/bin/sh
set -e
set -x
#yum clean metadata
yum update -y
yum install -y amazon-efs-utils zsh docker ecs-init git
yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm || true

systemctl enable docker
systemctl start docker
systemctl enable nfs
systemctl start nfs

cat >> /etc/fstab << EOF
fs-15a9c8bc.efs.us-west-2.amazonaws.com:/  /devel       nfs4    nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,_netdev,noresvport 0 0
fs-174024be.efs.us-west-2.amazonaws.com:/  /efs         nfs4    nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,_netdev,noresvport 0 0
EOF

mkdir -p /efs
mkdir -p /devel
mount -a
#[[ $(findmnt -M /devel) ]] ||  mount -t efs fs-15a9c8bc:/ /devel
#[[ $(findmnt -M /efs) ]] ||  mount -t efs fs-174024be:/ /efs

rm -f /etc/yum.repos.d/local.repo
cat << 'EOF' > /etc/yum.repos.d/local.repo
[local]
name=CentOS-$releasever - local packages for $basearch
baseurl=file:///efs/CentOS/7/local/$basearch
enabled=1
gpgcheck=0
protect=1
EOF

#yum install -y espa-processing

groupadd --gid 1000 cattelan || true
useradd --home-dir /efs/cattelan --no-create-home --shell /bin/zsh --uid 1000 --gid 1000 -G wheel -G docker --password $(openssl passwd -1 cattelan) cattelan || true
