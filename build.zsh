#!/bin/zsh

set -e 
set -o pipefail

SRC_DIR=$(realpath $(dirname "$0"))
BUILD_DIR=$HOME/build

echo "SRC_DIR:   $SRC_DIR"
echo "BUILD_DIR: $BUILD_DIR"

# c++
cd $BUILD_DIR
conan install $SRC_DIR/cpp -pr:b=default
cmake $SRC_DIR/cpp -G "Unix Makefiles" -DCMAKE_BUILD_TYPE=Release
cmake --build .

# # python
# cd $SRC_DIR/frontend
# python3 setup.py build
