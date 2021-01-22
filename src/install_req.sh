#!/bin/bash

set -eu

## works both under bash and sh
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")


pip3 install -r $SCRIPT_DIR/requirements.txt
