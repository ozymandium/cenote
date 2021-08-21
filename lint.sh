#!/bin/sh
black \
    ./scuba \
    ./scripts \
    ./test/python \
    --line-length 100 \
    -t py39