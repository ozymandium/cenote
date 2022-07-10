#!/bin/sh

# python stuff
black \
    ./cenote \
    ./test \
    --line-length 100 \
    -t py39

# c++ stuff
find ./bungee/ -iname *.h -o -iname *.cpp | xargs clang-format -i