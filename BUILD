load("@rules_python//python:pip.bzl", "pip_install")
load("@rules_python//python:defs.bzl", "py_binary")
load("@rules_python//python:defs.bzl", "py_library")
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
    name = "gas_usage",
    srcs = [
        "scuba/gas_usage.py",
    ],
    deps = [
        # requirement("pint"),        
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
