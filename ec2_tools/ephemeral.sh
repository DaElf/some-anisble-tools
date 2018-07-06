#!/bin/sh

### BEGIN INIT INFO
# Provides:          ephemeral
# Required-Start:    $syslog
# Required-Stop:     $syslog
# Should-Start:
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Encrypt and mount ephemeral storage
# Description:       No daemon is created or managed. This script is a Lucid
#                    creation that mounts AWS ephemeral volumes as encrypted,
#                    striped devices.
### END INIT INFO

VG_NAME=ephemeral
KEYDIR=/jobtmp

. /etc/init.d/functions

ephemeral_start() {
    DEVICES=$(readlink -f /dev/disk/by-id/nvme-Amazon_EC2_NVMe_Instance_Storage_*)
    PVSCAN_OUT=$(/sbin/pvscan)

    for device in $DEVICES; do
        if [ -z "$(/bin/echo "$PVSCAN_OUT" | grep " $device ")" ]; then
            /bin/umount "$device"
            /bin/sed -e "/$(basename $device)/d" -i /etc/fstab
            /bin/dd if=/dev/zero of="$device" bs=1M count=10
            /sbin/pvcreate "$device"
	else
	    vgchange -a y
        fi
    done

    if [ ! -d "/dev/$VG_NAME" ]; then
        /sbin/vgcreate "$VG_NAME" $DEVICES
    fi

    VGSIZE=$(/sbin/vgdisplay "$VG_NAME" | grep "Total PE" | sed -e "s/[^0-9]//g")

    [ ! -e "/dev/$VG_NAME/jobtmp" ] && /sbin/lvcreate -l100%FREE -njobtmp "$VG_NAME"

    /bin/mkdir -p "$KEYDIR"
    /bin/chmod 700 "$KEYDIR"

    /sbin/mkfs.xfs -f -Ljobtmp /dev/$VG_NAME/jobtmp || true
    [ -z "$(mount | grep " on /jobtmp ")" ] && rm -rf /jobtmp/*
    /bin/mount -t xfs /dev/$VG_NAME/jobtmp /jobtmp

    /bin/chmod 777 /jobtmp

} # ephemeral_start

ephemeral_stop() {
    /bin/umount /jobtmp

#    /sbin/vgchange -an "$VG_NAME"

} # ephemeral_stop


case "$1" in
  start)
        ephemeral_start
	;;

  stop)
        ephemeral_stop
	;;

  *)
	echo "Usage: /etc/init.d/ephemeral-mount {start|stop}"
	exit 1
esac

exit 0
