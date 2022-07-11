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

# nholthaus units library is header only
find_package(units)
target_link_libraries(bungee units)

install(
    TARGETS bungee 
    LIBRARY DESTINATION /usr/local/lib
    PUBLIC_HEADER DESTINATION /usr/local/include/bungee
)

