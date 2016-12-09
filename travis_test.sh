#! /bin/bash -x

cp .id_rsa ~/.ssh/id_rsa
cp .id_rsa.pub ~/.ssh/id_rsa.pub
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub
cat .id_rsa.pub >> ~/.ssh/authorized_keys

# set up ssh multiplexing
cp .travis_ssh_config ~/.ssh/config
mkdir -p ~/.ssh/controlmasters

# double check ntp works
mm-delay 10 ntpdate -quv time.stanford.edu

test/run.py --run-only setup
mm-delay 200 sh -c 'ssh -o "StrictHostKeyChecking=no" $USER@$MAHIMAHI_BASE exit; mm-loss uplink .1 mm-loss downlink .1 test/run.py --run-only test -r $USER@$MAHIMAHI_BASE:build/StanfordLPNG/pantheon'
