#!/bin/zsh

set -e 
set -o pipefail

SRC_DIR=$(realpath $(dirname "$0"))
BUILD_DIR=$HOME/build

echo "SRC_DIR:   $SRC_DIR"
echo "BUILD_DIR: $BUILD_DIR"

# c++
cd $BUILD_DIR
cmake $SRC_DIR/backend
make -j8
sudo make install

# # python
# cd $SRC_DIR/frontend
# python3 setup.py build
