#!/bin/zsh

set -e 
set -o pipefail

BUILD_DIR=$HOME/build

cd $BUILD_DIR
make test
