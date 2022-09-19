cmake_minimum_required(VERSION 3.22)

project(bungee VERSION 0.0.1 LANGUAGES CXX)

# # set this once conan removed?
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
# set(CMAKE_CXX_EXTENSIONS OFF)
# linker complains about fmt without this
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

#
# Dependencies
#

# gcov/lcov 
include(${CMAKE_BINARY_DIR}/CodeCoverage.cmake)

find_package(Python REQUIRED COMPONENTS Interpreter Development)

add_subdirectory(deps)

#
# Build shit
#

# set source/header files
file(GLOB_RECURSE SRC_FILES ${PROJECT_SOURCE_DIR}/src/bungee/*.cpp)
file(GLOB_RECURSE HDR_FILES ${PROJECT_SOURCE_DIR}/include/**/*.h)
file(GLOB_RECURSE TST_FILES ${PROJECT_SOURCE_DIR}/test/test_*.cpp)

# TODO: build and install units as separate library

## Core library 
# this is completely redundant, i didn't feel like fixing the linker path for the pybind module
# it literally compiles everything twice. gross.

add_library(bungee_core SHARED ${SRC_FILES})
target_link_libraries(bungee_core 
    PUBLIC
    Eigen3::Eigen
    fmt::fmt
)
target_include_directories(bungee_core PUBLIC include)

## Python bindings

# put everything in the python binding to avoid linker path problems and simply build flags
# for testing stuff
pybind11_add_module(bungee 
    ${HDR_FILES} # is this necessary?
    ${SRC_FILES}
    src/pybind.cpp
)
target_link_libraries(bungee 
    PUBLIC
        Eigen3::Eigen
        fmt::fmt
)
target_include_directories(bungee PUBLIC 
    include 
    ${pybind11_INCLUDE_DIRS}
)

## Installation

# this is done to allow the jupyter notebook to find the module without having to
# modify the python path
install(
    TARGETS bungee
    LIBRARY DESTINATION /home/user/.local/lib/python3.10/site-packages #??
)

## Testing

enable_testing()

function(bungee_unit_test test_name test_src)
    add_executable(${test_name} ${test_src})
    target_link_libraries(${test_name} bungee_core GTest::gtest_main)
    add_test(${test_name} ${test_name})
endfunction()

bungee_unit_test(test_water test/test_Water.cpp)
bungee_unit_test(test_tank test/test_Tank.cpp)
bungee_unit_test(test_scr test/test_Scr.cpp)
bungee_unit_test(test_plan test/test_Plan.cpp)
bungee_unit_test(test_result test/test_Result.cpp)
bungee_unit_test(test_models test/test_Models.cpp)
bungee_unit_test(test_compartment test/test_Compartment.cpp)
bungee_unit_test(test_buhlmann test/test_Buhlmann.cpp)

# coverage
append_coverage_compiler_flags()
setup_target_for_coverage_gcovr_html(
    NAME bungee_coverage
    EXECUTABLE 
        make test
)
