cmake_minimum_required(VERSION 3.22)

project(bungee VERSION 0.0.1 LANGUAGES CXX)

# # set this once conan removed?
# set(CMAKE_CXX_STANDARD 20)
# set(CMAKE_CXX_STANDARD_REQUIRED ON)
# set(CMAKE_CXX_EXTENSIONS OFF)
# linker complains about fmt without this
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

#
# Dependencies
#

# conan
include(${CMAKE_BINARY_DIR}/conan_toolchain.cmake)

# gcov/lcov 
include(CodeCoverage)

## get dependencies from conan
find_package(units CONFIG REQUIRED)
# find_package(Eigen3 CONFIG REQUIRED)
find_package(pybind11 CONFIG REQUIRED)
find_package(Python REQUIRED COMPONENTS Interpreter Development)

## FetchContent dependencies

include(FetchContent)

FetchContent_Declare(
      Eigen
      GIT_REPOSITORY    https://gitlab.com/libeigen/eigen.git
      GIT_TAG           3.4.0
    )
FetchContent_MakeAvailable(Eigen)

FetchContent_Declare(fmt
  GIT_REPOSITORY https://github.com/fmtlib/fmt.git
  GIT_TAG 9.1.0
)
FetchContent_MakeAvailable(fmt)

FetchContent_Declare(
  googletest
  GIT_REPOSITORY https://github.com/google/googletest.git
  GIT_TAG release-1.12.1
)
FetchContent_MakeAvailable(googletest)
include(GoogleTest)

#
# Build shit
#

# set source/header files
file(GLOB_RECURSE SRC_FILES ${PROJECT_SOURCE_DIR}/src/bungee/*.cpp)
file(GLOB_RECURSE HDR_FILES ${PROJECT_SOURCE_DIR}/include/bungee/*.h)

## Core library 
# this is completely redundant, i didn't feel like fixing the linker path for the pybind module
# it literally compiles everything twice. gross.

add_library(bungee_core SHARED ${SRC_FILES})
target_link_libraries(bungee_core 
    PUBLIC
    units::units # header only, but whatever
    Eigen3::Eigen
    fmt::fmt
)
target_include_directories(bungee_core PUBLIC 
    include 
    ${units_INCLUDE_DIRS}
)

## Python bindings

# conan fucking sucks
# https://github.com/conan-io/conan-center-index/issues/9343
if(NOT COMMAND pybind11_add_module)
    foreach(INCDIR IN LISTS pybind11_INCLUDE_DIRS)
        if(EXISTS "${INCDIR}/../lib/cmake/pybind11/pybind11Tools.cmake")
            include("${INCDIR}/../lib/cmake/pybind11/pybind11Common.cmake")
            include("${INCDIR}/../lib/cmake/pybind11/pybind11Tools.cmake")
            break()
        elseif(EXISTS "${INCDIR}/../../lib/cmake/pybind11/pybind11Tools.cmake")
            include("${INCDIR}/../../lib/cmake/pybind11/pybind11Common.cmake")
            include("${INCDIR}/../../lib/cmake/pybind11/pybind11Tools.cmake")
            break()
        endif()
    endforeach()
endif()

# put everything in the python binding to avoid linker path problems and simply build flags
# for testing stuff
pybind11_add_module(bungee 
    ${HDR_FILES} # is this necessary?
    ${SRC_FILES}
    src/pybind.cpp
)
target_link_libraries(bungee 
    PUBLIC
    units::units
    Eigen3::Eigen
    fmt::fmt
)
target_include_directories(bungee PUBLIC 
    include 
    ${units_INCLUDE_DIRS}
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
