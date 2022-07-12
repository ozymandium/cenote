#!/bin/sh

set -e 
set -o pipefail

SRC_DIR=$(dirname -- "$( readlink -f -- "$0"; )";)

docker build --tag=cenote $SRC_DIR

docker run --interactive --tty --rm \
  --volume "$SRC_DIR":/home/user/src \
  --volume $HOME/.gitconfig:/etc/gitconfig \
  --entrypoint /bin/zsh \
  cenote
