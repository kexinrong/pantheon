#! /bin/bash -x

mkdir -p ~/.ssh
cp .id_rsa ~/.ssh/id_rsa
cp .id_rsa.pub ~/.ssh/id_rsa.pub
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub
cat .id_rsa.pub >> ~/.ssh/authorized_keys
test/setup.py default_tcp
PANTHEON_DIR=$(pwd)
echo $PANTHEON_DIR

mm-delay 5 sh -c 'ssh -o "StrictHostKeyChecking=no" $USER@$MAHIMAHI_BASE exit; mm-loss uplink .1 mm-loss downlink .1 test/test.py default_tcp -r $USER@$MAHIMAHI_BASE:build/StanfordLPNG/pantheon'
