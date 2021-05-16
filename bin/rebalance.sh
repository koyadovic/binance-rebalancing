#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd $SCRIPT_DIR
cd ..

wait_seconds=$((120 + $RANDOM % 120))
echo Waiting aleatory $wait_seconds seconds ...
sleep $wait_seconds

source ~/.bash_profile
source ~/.bashrc

# environment variables
source .environment

# execute it
python rebalance.py --yes &> /tmp/rebalance.output
date >> /tmp/rebalance.output
