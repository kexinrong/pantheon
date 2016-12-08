#! /bin/bash
#test/setup.py default_tcp
mm-delay 5 sh -c 'ssh -o "StrictHostKeyChecking=no" $USER@$MAHIMAHI_BASE exit; mm-delay 5 ping -c 5 $MAHIMAHI_BASE'
