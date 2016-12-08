#! /bin/bash
#test/setup.py default_tcp
cat ~/.ssh/id_rsa.pub
mkdir -p ~/.ssh
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
mm-delay 5 sh -c 'ssh -o "StrictHostKeyChecking=no" $USER@$MAHIMAHI_BASE exit; mm-delay 5 test/run.pyping -c 5 $MAHIMAHI_BASE'
