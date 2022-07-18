cmake_minimum_required(VERSION 3.10)

project(bungee VERSION 0.0.1 LANGUAGES CXX)

# conan
include(${CMAKE_BINARY_DIR}/conan_toolchain.cmake)

# set source/header files
file(GLOB SRC_FILES ${PROJECT_SOURCE_DIR}/src/bungee/*.cpp)
file(GLOB HDR_FILES ${PROJECT_SOURCE_DIR}/include/bungee/*.h)

## get dependencies
find_package(units CONFIG REQUIRED)
find_package(GTest CONFIG REQUIRED)
find_package(Eigen3 CONFIG REQUIRED)
find_package(pybind11 CONFIG REQUIRED)
find_package(Python REQUIRED COMPONENTS Interpreter Development)

## Python bindings

# instead of building the python bindings as a thin library that links to the main library
# do a redundant python library that includes because i can't figure out how to get the linker
# to find libbungee.so and am pretty fucking done with build system problems. jesus christ just
# let me write code already.

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

pybind11_add_module(bungee 
    ${HDR_FILES}
    ${SRC_FILES}
    src/pybind.cpp
)
target_link_libraries(bungee 
    PUBLIC
    ${units_LIBRARIES} # header only, but whatever
    ${Eigen3_LIBRARIES}
    ${pybind11_LIBRARIES}
)
target_include_directories(bungee PUBLIC 
    include 
    ${units_INCLUDE_DIRS}
    ${Eigen3_INCLUDE_DIRS}
    ${pybind11_INCLUDE_DIRS}
)

## Installation

install(
    TARGETS bungee
    LIBRARY DESTINATION /home/user/.local/lib/python3.10/site-packages #??
)

## Testing

# enable_testing()

# # Water.cpp
# add_executable(test_water test/test_Water.cpp)
# target_link_libraries(test_water GTest::GTest GTest::Main bungee)
# add_test(test-water test_water)

# # Tank.cpp
# add_executable(test_tank test/test_Tank.cpp)
# target_link_libraries(test_tank GTest::GTest GTest::Main bungee)
# add_test(test-tank test_tank)

# # Scr.cpp
# add_executable(test_scr test/test_Scr.cpp)
# target_link_libraries(test_scr GTest::GTest GTest::Main bungee)
# add_test(test-scr test_scr)

# # Plan.cpp
# add_executable(test_plan test/test_Plan.cpp)
# target_link_libraries(test_plan GTest::GTest GTest::Main bungee)
# add_test(test-plan test_plan)

# # Result.cpp
# add_executable(test_result test/test_Result.cpp)
# target_link_libraries(test_result GTest::GTest GTest::Main bungee)
# add_test(test-result test_result)
