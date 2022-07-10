#!/bin/sh

DEP_DIR=$1

# install gsl-lite
wget https://github.com/gsl-lite/gsl-lite/archive/refs/tags/v0.40.0.tar.gz -O /tmp/gsl-lite.tar.gz
tar -xf /tmp/gsl-lite.tar.gz -C ${DEP_DIR}
GSL_LITE_BUILD_DIR=$DEP_DIR/gsl-lite-0.40.0/build
mkdir $GSL_LITE_BUILD_DIR
cd $GSL_LITE_BUILD_DIR
cmake ..
sudo make install

# install mp-units
wget https://github.com/mpusz/units/archive/refs/tags/v0.7.0.tar.gz -O /tmp/units.tar.gz
tar -xf /tmp/units.tar.gz -C ${DEP_DIR}
MP_UNITS_BUILD_DIR=$DEP_DIR/units-0.7.0/build
mkdir $MP_UNITS_BUILD_DIR
cd $MP_UNITS_BUILD_DIR
# cmake ..
# sudo make install
