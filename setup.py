from setuptools import setup, find_packages

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
)
