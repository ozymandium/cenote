cmake_minimum_required(VERSION 3.10)

project(bungee VERSION 0.0.1 LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# set source files
file(GLOB SRC_FILES ${PROJECT_SOURCE_DIR}/src/*.cpp)
# # set header files
file(GLOB HDR_FILES ${PROJECT_SOURCE_DIR}/include/bungee/*.h)

# the pybind11 library has to be shared, but dependencies of the pybind11 module
# can be static https://github.com/pybind/pybind11/issues/466#issuecomment-256386257
add_library(bungee STATIC ${SRC_FILES})
target_include_directories(bungee PUBLIC include)
set_target_properties(bungee PROPERTIES PUBLIC_HEADER "${HDR_FILES}")

# nholthaus units library is header only, and installed in /usr/local/include
# TODO really ought to do find_package and whatnot here..
find_package(units REQUIRED)

install(
    TARGETS bungee 
    LIBRARY DESTINATION /usr/local/lib
    PUBLIC_HEADER DESTINATION /usr/local/include/bungee
)

## Testing

enable_testing()

# Water.cpp
find_package(GTest REQUIRED)
add_executable(test_water test/test_Water.cpp)
target_link_libraries(test_water GTest::GTest GTest::Main bungee)
add_test(test-water test_water)