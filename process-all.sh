#!/bin/bash

set -eu


## works both under bash and sh
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")


$SCRIPT_DIR/doc/generate-doc.sh

$SCRIPT_DIR/examples/generate.sh

$SCRIPT_DIR/src/testrsscast/runtests.py

$SCRIPT_DIR/tools/checkall.sh


echo "processing completed"
