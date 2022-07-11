#!/bin/zsh

set -e 
set -o pipefail

# python stuff
black \
    ./frontend/cenote \
    ./frontend/test \
    --line-length 100 \
    -t py39

# c++ stuff
find . -regex '.*\.\(cpp\|h\|inl\)' -exec clang-format -i {} \;
