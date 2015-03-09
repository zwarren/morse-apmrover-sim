#!/usr/bin/env bash

# http://stackoverflow.com/questions/59895/can-a-bash-script-tell-what-directory-its-stored-in
SIM_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

MORSE_SIM_DIR="${SIM_DIR}/RoverSim"

export MORSE_RESOURCE_PATH="$MORSE_SIM_DIR/data:$SIM_DIR"

# don't know why, but having a PYTHONPATH end with colon does not work,
# so make to prepend only when a PYTHONPATH is already set.
if [ -n "$PYTHONPATH" ] ; then
    export PYTHONPATH="$MORSE_SIM_DIR/src:$PYTHONPATH"
else
    export PYTHONPATH="$MORSE_SIM_DIR/src"
fi

echo MORSE_RESOURCE_PATH=$MORSE_RESOURCE_PATH
echo PYTHONPATH=$PYTHONPATH

morse run "${MORSE_SIM_DIR}/default.py"
#${MORSE_SIM_DIR}/default.py
