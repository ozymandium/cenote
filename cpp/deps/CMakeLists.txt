include(FetchContent)

# because eigen build needs to disable tests with a flag shared by this project, eigen dependency
# is declared in a subdirectory
add_subdirectory(eigen)

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
