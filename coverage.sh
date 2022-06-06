#!/bin/sh

set -e 
set -o pipefail

coverage run setup.py test
coverage report -m