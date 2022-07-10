from setuptools import setup, find_packages
from pybind11.setup_helpers import Pybind11Extension
from glob import glob

setup(
    name = "cenote",
    version = "0.0.1",
    description = "Dive planner",
    packages = find_packages(),
    python_requires = ">=3.6",
    entry_points = {
        "console_scripts": [
            "scr-from-sac = cenote.util.scr_from_sac:main",
            "sac-from-scr = cenote.util.sac_from_scr:main",
            "plot = cenote.util.plot:main",
            "mod = cenote.util.mod:main",
        ],
    },
    test_suite = "test",
    ext_modules=[
        Pybind11Extension(
            "bungee",
            [
                "bungee/src/Buhlmann.cpp",
                "bungee/src/Compartment.cpp",
                "bungee/src/CompartmentManager.cpp",
                "bungee/src/Mix.cpp",
                "bungee/src/Models.cpp",
                "bungee/src/Water.cpp",
                "bungee/pybind.cpp",
            ],
            include_dirs = [
                "bungee/include",
            ],
            cxx_std=17,
        )
    ],
)
