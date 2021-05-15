#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd $SCRIPT_DIR
cd ..

source ~/.bash_profile
source ~/.bashrc

# environment variables
source .environment

# execute it
python rebalance.py --yes &> /tmp/rebalance.output
date >> /tmp/rebalance.output
