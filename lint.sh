#!/bin/sh
black \
    ./scuba \
    test/python \
    --line-length 100 \
    -t py39