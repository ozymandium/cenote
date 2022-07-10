#!/bin/sh

# python stuff
black \
    ./frontend/cenote \
    ./frontend/test \
    --line-length 100 \
    -t py39

# c++ stuff
find ./backend/bungee/ -iname *.h -o -iname *.cpp | xargs clang-format -i
