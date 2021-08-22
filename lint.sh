#!/bin/sh
black \
    ./cenote \
    ./scripts \
    ./test/python \
    --line-length 100 \
    -t py39