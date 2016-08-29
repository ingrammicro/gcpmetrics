#!/usr/bin/env bash

# force stop on errors
set -e

# making sure we run under Jenkins
if [ -z "$BUILD_NUMBER" ]
then
    echo "Error: BUILD_NUMBER variable is not defined (script was designed to run under Jenkins)."
    echo "Terminating..."
    exit 1
fi

# generating version identifier
PACKAGE_VERSION="1.0.$BUILD_NUMBER"
echo "Generating version.txt file ($PACKAGE_VERSION)..."
echo "$PACKAGE_VERSION" > version.txt

# version information is here for logging purposes:
# python 2.7+ is required to package properly
python --version
flake8 --version

# nice color constants
RED_COLOR='\033[0;31m'
NO_COLOR='\033[0m'

# check syntax (and highlight output)
printf "${RED_COLOR}"
flake8 .
printf "${NO_COLOR}"

# build doc and src packages
python setup.py publish $@
