load("@rules_python//python:defs.bzl", "py_binary")
load("@rules_python//python:defs.bzl", "py_library")

# # Attempting to get PIP installation to work.
# load("@rules_python//python:pip.bzl", "pip_install")
# load("@pip//:requirements.bzl", "requirement")
# pip_install(
#    name = "pip_deps",
#    requirements = "requirements.txt",
# )
# # # Load the starlark macro which will define your dependencies.
# # load("@pip_deps//:requirements.bzl", "install_deps")
# # # Call it to define repos for your requirements.
# # install_deps()
# load("@pip_deps//:requirements.bzl", "pip_install")
# pip_install()
# load python build rules
# load("@pip_deps//:requirements.bzl", "requirement")

py_library(
    name = "scuba",
    srcs = [
        "scuba/__init__.py",
        "scuba/config.py",
        "scuba/gas_usage.py",
    ],
    deps = [
        # requirement("pint"),        
    ],
)

# scripts

py_binary(
    name = "calc_gas_usage",
    srcs = [
        "scripts/calc_gas_usage.py",
    ],
    deps = [
        ":scuba",
    ],
)

py_binary(
    name = "calc_scr",
    srcs = [
        "scripts/calc_scr.py",
    ],
    deps = [
        ":scuba",
    ],
)

# tests... need to figure out how to write tests

py_binary(
    name = "test_gas_usage",
    srcs = [
        "test/python/test_gas_usage.py",
    ],
    deps = [
        ":scuba",
    ],
)
