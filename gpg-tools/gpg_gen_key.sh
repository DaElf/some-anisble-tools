#!/usr/bin/env sh
set -x
#export GNUPGHOME=$(mktemp -d /tmp/$0.XXXXXX)
export GNUPGHOME=$(pwd)/local-gnupg

[ -d $GNUPGHOME ] || mkdir -p $GNUPGHOME
chmod 700 $GNUPGHOME

#gpg --no-option --batch --generate-key gpg-gen-key-input
gpg --no-option --batch --gen-key gpg-gen-key-input
gpg --no-option --export-secret-keys --output USGS_private.gpg
gpg --no-option --export --output USGS_public.gpg

gpg --no-option --armor --export --output USGS_public.asc
gpg --no-option --armor --export-secret-keys --output USGS_private.asc
