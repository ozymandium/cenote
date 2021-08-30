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
    name = "cenote",
    srcs = [
        "cenote/__init__.py",
        "cenote/config.py",
        "cenote/gas_usage.py",
        "cenote/parse/__init__.py",
        "cenote/parse/shearwater_xml.py",
        "cenote/parse/yaml.py",

    ],
    deps = [
        # requirement("pint"),        
    ],
)

py_library

# scripts

py_binary(
    name = "calc_gas_usage",
    srcs = [
        "cenote/util/calc_gas_usage.py",
    ],
    deps = [
        ":cenote",
    ],
)

py_binary(
    name = "scr_from_sac",
    srcs = [
        "cenote/util/scr_from_sac.py",
    ],
    deps = [
        ":cenote",
    ],
)

py_binary(
    name = "sac_from_scr",
    srcs = [
        "cenote/util/sac_from_scr.py",
    ],
    deps = [
        ":cenote",
    ],
)

py_binary(
    name = "shearwater_xml_to_yaml",
    srcs = [
        "cenote/util/shearwater_xml_to_yaml.py",
    ],
    deps = [
        ":cenote",
    ]
)

# tests... need to figure out how to write tests

py_binary(
    name = "test_gas_usage",
    srcs = [
        "test/python/test_gas_usage.py",
    ],
    deps = [
        ":cenote",
    ],
)
