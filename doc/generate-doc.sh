#!/bin/bash

set -eu


## works both under bash and sh
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")


SRC_DIR="$SCRIPT_DIR/../src"


generate_help() {
    HELP_PATH=$SCRIPT_DIR/cmdargs.md
    
    echo "## <a name=\"main_help\"></a> startrsscast --help" > ${HELP_PATH}
    echo -e "\`\`\`" >> ${HELP_PATH}
    $SRC_DIR/startrsscast --help >> ${HELP_PATH}
    echo -e "\`\`\`" >> ${HELP_PATH}
}


generate_help


$SCRIPT_DIR/generate_small.sh


$SCRIPT_DIR/../tools/mdpreproc.py $SCRIPT_DIR/../README.md
