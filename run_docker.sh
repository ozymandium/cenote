#!/bin/sh

# Before executing this:
#   sudo chown -R $USER ~/.buildozer
#   rm -rf ~/.buildozer && mkdir ~/.buildozer

set -e 
set -o pipefail

SRC_DIR=$(dirname -- "$( readlink -f -- "$0"; )";)
echo "SRC_DIR=${SRC_DIR}"

docker build --tag=cenote $SRC_DIR

docker run --interactive --tty --rm \
  --volume "$HOME/.buildozer":/home/user/.buildozer \
  --volume "$SRC_DIR":/home/user/src \
  --entrypoint /bin/zsh \
  cenote
