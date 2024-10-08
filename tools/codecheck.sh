#!/bin/bash

#set -eu
set -u


## works both under bash and sh
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")


src_dir=$SCRIPT_DIR/../src


echo "code checking using pycodestyle"

## E115 intend of comment
## E126 continuation line over-indented for hanging indent
## E201 whitespace after '('
## E202 whitespace before ')'
## E221 multiple spaces before equal operator
## E241 multiple spaces after ':'
## E262 inline comment should start with '# '
## E265 block comment should start with '# '
## E266 too many leading '#' for block comment
## E402 module level import not at top of file
## E501 line too long (80 > 79 characters)
## W391 blank line at end of file
## D    all docstyle checks
ignore_errors=E115,E126,E201,E202,E221,E241,E262,E265,E266,E402,E501,W391,D


pycodestyle --show-source --statistics --count --ignore=$ignore_errors $src_dir
exit_code=$?

if [ $exit_code -ne 0 ]; then
    exit $exit_code
fi

echo "pycodestyle -- no warnings found"


echo "code checking using flake8"

## F401 'PyQt5.QtCore' imported but unused
ignore_errors=$ignore_errors,F401

python3 -m flake8 --show-source --statistics --count --ignore=$ignore_errors $src_dir
exit_code=$?

if [ $exit_code -ne 0 ]; then
    echo -e "\nflake8 errors found"
    exit $exit_code
fi

echo "flake8 -- no warnings found"


echo "code checking using pylint3"
echo "for inline suppression use: # pylint: disable=<check-code>"

pylint --rcfile=$SCRIPT_DIR/pylint3.config $src_dir/rsscast $src_dir/testrsscast $src_dir/*.py
exit_code=$?
if [ $exit_code -ne 0 ]; then
    exit $exit_code
fi
echo "pylint3 -- no warnings found"
