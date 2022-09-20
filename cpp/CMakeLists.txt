cmake_minimum_required(VERSION 3.22)

project(bungee VERSION 0.0.1 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
# linker complains about fmt without this
set(CMAKE_POSITION_INDEPENDENT_CODE ON) 
# the pybind module cannot find the core library without this, as the runtime path is stripped when
# set to false
SET(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)

## Dependencies

include(${CMAKE_BINARY_DIR}/CodeCoverage.cmake)
find_package(Python REQUIRED COMPONENTS Interpreter Development)
add_subdirectory(deps)

## Build

# Core library 
file(GLOB_RECURSE SRC_FILES ${PROJECT_SOURCE_DIR}/src/bungee/*.cpp)
add_library(bungee_core SHARED ${SRC_FILES})
target_link_libraries(bungee_core 
    PUBLIC
    Eigen3::Eigen
    fmt::fmt
    units
)
target_include_directories(bungee_core PUBLIC include)

# Python bindings
add_library(bungee MODULE src/pybind.cpp)
target_link_libraries(bungee PUBLIC bungee_core pybind11::module)
target_link_directories(bungee PUBLIC /usr/local/lib)

## Installation

# this is done to allow the jupyter notebook to find the module without having to
# modify the python path. for use beyond just the jupyter notebook, it needs to be installed
# for real.
install(
    TARGETS bungee
    COMPONENT python
    LIBRARY DESTINATION /home/user/.local/lib/python3.10/site-packages # TODO set this using the site dir results
)
install(
    TARGETS bungee_core
)

## Testing

enable_testing()

file(GLOB_RECURSE TEST_FILES ${PROJECT_SOURCE_DIR}/test/test_*.cpp)
foreach(TEST_FILE ${TEST_FILES})
    get_filename_component(TEST_NAME ${TEST_FILE} NAME_WE)
    message("Found test: ${TEST_NAME}")
    add_executable(${TEST_NAME} ${TEST_FILE})
    target_link_libraries(${TEST_NAME} bungee_core GTest::gtest_main)
    add_test(${TEST_NAME} ${TEST_NAME})
endforeach()

# coverage
append_coverage_compiler_flags()
setup_target_for_coverage_gcovr_html(
    NAME bungee_coverage
    EXECUTABLE 
        make test
)
