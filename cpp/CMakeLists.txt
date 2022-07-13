cmake_minimum_required(VERSION 3.10)

project(bungee VERSION 0.0.1 LANGUAGES CXX)

# conan
include(${CMAKE_BINARY_DIR}/conan_toolchain.cmake)

# set source/header files
file(GLOB SRC_FILES ${PROJECT_SOURCE_DIR}/src/*.cpp)
file(GLOB HDR_FILES ${PROJECT_SOURCE_DIR}/include/bungee/*.h)

# get dependencies
find_package(units CONFIG REQUIRED)
find_package(GTest REQUIRED)
find_package(mp-units CONFIG REQUIRED)

# the pybind11 library has to be shared, but dependencies of the pybind11 module
# can be static https://github.com/pybind/pybind11/issues/466#issuecomment-256386257
add_library(bungee STATIC ${SRC_FILES})
target_link_libraries(bungee 
    ${mp-units_LIBRARIES}

)
target_include_directories(bungee PUBLIC 
    include 
    ${units_INCLUDE_DIRS}
    ${mp-units_INCLUDE_DIR}
    ${mp-units_INCLUDE_DIRS}
)
set_target_properties(bungee PROPERTIES PUBLIC_HEADER "${HDR_FILES}")
target_compile_features(bungee PUBLIC cxx_std_20)

install(
    TARGETS bungee 
    LIBRARY DESTINATION /usr/local/lib
    PUBLIC_HEADER DESTINATION /usr/local/include/bungee
)

## Testing

enable_testing()

# Water.cpp
add_executable(test_water test/test_Water.cpp)
target_link_libraries(test_water GTest::GTest GTest::Main bungee)
add_test(test-water test_water)

# Tank.cpp
add_executable(test_tank test/test_Tank.cpp)
target_link_libraries(test_tank GTest::GTest GTest::Main bungee)
add_test(test-tank test_tank)

# Scr.cpp
add_executable(test_scr test/test_Scr.cpp)
target_link_libraries(test_scr 
    GTest::GTest GTest::Main 
    ${mp-units_LIBRARIES}
)
target_include_directories(test_scr PUBLIC 
    ${mp-units_INCLUDE_DIR}
    ${mp-units_INCLUDE_DIRS}
)
add_test(test-scr test_scr)