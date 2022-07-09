#!/bin/sh

# python stuff
black \
    ./lib/cenote \
    ./lib/test \
    --line-length 100 \
    -t py39

# c++ stuff
find ./lib/bungee/ -iname *.h -o -iname *.cpp | xargs clang-format -i