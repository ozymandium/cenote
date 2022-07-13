#!/bin/zsh

set -e 
set -o pipefail

# python stuff
black \
    ./py/cenote \
    ./py/test \
    --line-length 100 \
    -t py39

# c++ stuff
find cpp -regex '.*\.\(cpp\|h\|inl\)' -exec clang-format -i {} -style=file:./.clang-format \;
