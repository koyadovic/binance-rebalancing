#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd $SCRIPT_DIR
cd ..

if test -f ~/.bash_profile; then
    source ~/.bash_profile
fi

if test -f ~/.bashrc; then
    source ~/.bashrc
fi

# environment variables
if test -f .environment; then
    source .environment
fi

# python virtualenv
if test -f env/bin/activate; then
    source env/bin/activate
fi

# execute it
python rebalance.py --yes &> /tmp/rebalance.output
date >> /tmp/rebalance.output
