#! /bin/bash
#test/setup.py default_tcp
mkdir -p ~/.ssh
cp .id_rsa ~/.ssh/id_rsa
cp .id_rsa.pub ~/.ssh/id_rsa.pub
cat .id_rsa >> ~/.ssh/authorized_keys
mm-delay 5 sh -c 'ssh -o "StrictHostKeyChecking=no" $USER@$MAHIMAHI_BASE exit; mm-delay 5 test/run.pyping -c 5 $MAHIMAHI_BASE'
