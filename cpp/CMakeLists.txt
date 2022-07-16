cmake_minimum_required(VERSION 3.10)

project(bungee VERSION 0.0.1 LANGUAGES CXX)

# conan
include(${CMAKE_BINARY_DIR}/conan_toolchain.cmake)

# set source/header files
file(GLOB SRC_FILES ${PROJECT_SOURCE_DIR}/src/*.cpp)
file(GLOB HDR_FILES ${PROJECT_SOURCE_DIR}/include/bungee/*.h)

# get dependencies
find_package(units CONFIG REQUIRED)
find_package(GTest CONFIG REQUIRED)
find_package(Eigen3 CONFIG REQUIRED)
find_package(pybind11 CONFIG REQUIRED)
find_package(Python REQUIRED COMPONENTS Interpreter Development)

## Core library

# the pybind11 library has to be shared, but dependencies of the pybind11 module
# can be static https://github.com/pybind/pybind11/issues/466#issuecomment-256386257
# make it static for packing, shared for faster dev
# add_library(bungee STATIC ${SRC_FILES})
add_library(bungee SHARED ${SRC_FILES})
target_link_libraries(bungee 
    ${units_LIBRARIES} # header only, but whatever
    ${Eigen3_LIBRARIES}
    ${pybind11_LIBRARIES}
    ${Python_LIBRARIES}
)
target_include_directories(bungee PUBLIC 
    include 
    ${units_INCLUDE_DIRS}
    ${Eigen3_INCLUDE_DIRS}
    ${pybind11_INCLUDE_DIRS}
    ${Python_INCLUDE_DIRS}
)
set_target_properties(bungee PROPERTIES PUBLIC_HEADER "${HDR_FILES}")
target_compile_features(bungee PUBLIC cxx_std_20)

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

pybind11_add_module(bungee_py src/pybind.cpp)
target_link_libraries(bungee_py PRIVATE bungee)

## Installation

install(
    TARGETS bungee 
    LIBRARY DESTINATION /usr/local/lib
    PUBLIC_HEADER DESTINATION /usr/local/include/bungee
)

# ## Testing

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
