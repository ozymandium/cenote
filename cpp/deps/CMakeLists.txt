include(FetchContent)

# eigen dep pulled in a separate file to prevent eigen tests from running. they are controlled with
# a global variable and not an eigen-specific variable, so disabling them in the top level cmake
# also interferes with project tests
include(FetchContent)
FetchContent_Declare(
  Eigen
  GIT_REPOSITORY https://gitlab.com/libeigen/eigen.git
  GIT_TAG 3.4.0
  GIT_SHALLOW TRUE
  GIT_PROGRESS TRUE
)
set(EIGEN_BUILD_DOC OFF)
set(EIGEN_BUILD_PKGCONFIG OFF)
FetchContent_MakeAvailable(Eigen)

# fmt
FetchContent_Declare(
    fmt
    GIT_REPOSITORY      https://github.com/fmtlib/fmt.git
    GIT_TAG             9.1.0
)
FetchContent_MakeAvailable(fmt)

# pybind
FetchContent_Declare(
    pybind11
    GIT_REPOSITORY  https://github.com/pybind/pybind11.git
    GIT_TAG         v2.9.2
)
FetchContent_MakeAvailable(pybind11)

# gtest
FetchContent_Declare(
  googletest
  GIT_REPOSITORY    https://github.com/google/googletest.git
  GIT_TAG           release-1.12.1
)
FetchContent_MakeAvailable(googletest)
include(GoogleTest)

# units
add_subdirectory(units)

# protobuf
find_package(Protobuf REQUIRED)
include_directories(${Protobuf_INCLUDE_DIRS})
include_directories(${CMAKE_CURRENT_BINARY_DIR})
