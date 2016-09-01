#!/usr/bin/env bash

# force stop on errors
set -e

# making sure we run under Jenkins
if [ -z "$BUILD_NUMBER" ]
then
    if [ -z "$TRAVIS_BUILD_NUMBER" ]
    then
        echo "Error: BUILD_NUMBER and TRAVIS_BUILD_NUMBER not defined!"
        echo "This  script was designed to run in either Jenkins CI or Travis CI."
        echo "Terminating..."
        exit 1
    fi
    export BUILD_NUMBER=$TRAVIS_BUILD_NUMBER
fi

# generating version identifier
PACKAGE_VERSION="1.0.$BUILD_NUMBER"
echo "Generating VERSION file ($PACKAGE_VERSION)..."
echo "$PACKAGE_VERSION" > ./gcpmetrics/VERSION

if [ -z "$TRAVIS_BUILD_NUMBER" ]
then
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
fi

