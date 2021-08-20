# use rules_python to install pip deps
load("@rules_python//python:pip.bzl", "pip_install")
pip_install(
   name = "pip_deps",
   requirements = "//:requirements.txt",
)
# Load the starlark macro which will define your dependencies.
load("@pip_deps//:requirements.bzl", "install_deps")
# Call it to define repos for your requirements.
install_deps()

# load python build rules
load("@rules_python//python:defs.bzl", "py_binary")
load("@rules_python//python:defs.bzl", "py_library")

py_library(
    name = "gas_usage",
    deps = [
        ":pip_deps",
    ],
)

py_binary(
    name = "calc_gas_usage",
    srcs = [
        "scripts/calc_gas_usage.py",
    ],
    deps = [
        ":gas_usage",
    ],
)
