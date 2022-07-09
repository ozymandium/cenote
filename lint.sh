#!/bin/sh

# python stuff
black \
    ./lib/cenote \
    ./lib/test \
    --line-length 100 \
    -t py39

# c++ stuff
clang-format -i ./lib/bungee/include/bungee/Buhlmann.h
clang-format -i ./lib/bungee/include/bungee/Compartment.h
clang-format -i ./lib/bungee/src/Buhlmann.cpp
clang-format -i ./lib/bungee/src/Compartment.cpp