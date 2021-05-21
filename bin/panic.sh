#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd $SCRIPT_DIR
cd ..

source ~/.bash_profile
source ~/.bashrc

# environment variables
source .environment

# execute it
python panic.py &> /tmp/panic.output
date >> /tmp/panic.output
