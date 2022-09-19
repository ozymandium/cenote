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

## get dependencies from conan
find_package(Python REQUIRED COMPONENTS Interpreter Development)

add_subdirectory(deps)

#
# Build shit
#

# set source/header files
file(GLOB_RECURSE SRC_FILES ${PROJECT_SOURCE_DIR}/src/bungee/*.cpp)
file(GLOB_RECURSE HDR_FILES ${PROJECT_SOURCE_DIR}/include/**/*.h)

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

# Water.cpp
add_executable(test_water test/test_Water.cpp)
target_link_libraries(test_water bungee_core GTest::gtest_main)
gtest_discover_tests(test_water)

# # Tank.cpp
add_executable(test_tank test/test_Tank.cpp)
target_link_libraries(test_tank bungee_core GTest::gtest_main)
gtest_discover_tests(test_tank)

# # Scr.cpp
add_executable(test_scr test/test_Scr.cpp)
target_link_libraries(test_scr bungee_core GTest::gtest_main)
gtest_discover_tests(test_scr)

# # Plan.cpp
add_executable(test_plan test/test_Plan.cpp)
target_link_libraries(test_plan bungee_core GTest::gtest_main)
gtest_discover_tests(test_plan)

# # Result.cpp
add_executable(test_result test/test_Result.cpp)
target_link_libraries(test_result bungee_core GTest::gtest_main)
gtest_discover_tests(test_result)

# # Models.cpp
add_executable(test_models test/test_Models.cpp)
target_link_libraries(test_models bungee_core GTest::gtest_main)
gtest_discover_tests(test_models)

# # Compartment.cpp
add_executable(test_compartment test/test_Compartment.cpp)
target_link_libraries(test_compartment bungee_core GTest::gtest_main)
gtest_discover_tests(test_compartment)

# # Buhlmann.cpp
add_executable(test_buhlmann test/test_Buhlmann.cpp)
target_link_libraries(test_buhlmann bungee_core GTest::gtest_main)
gtest_discover_tests(test_buhlmann)

# coverage
append_coverage_compiler_flags()
setup_target_for_coverage_gcovr_html(
    NAME bungee_coverage
    EXECUTABLE 
        make test
)
