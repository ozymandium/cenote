from setuptools import setup, find_packages
import os

setup(
    name = "cenote",
    version = "0.0.2",
    description = "Dive planner",
    packages = find_packages(),
    python_requires = ">=3.10",
    # build_dir=os.path.join(os.environ["BUILD_DIR"], "py", "build"),
    # dist_dir=os.path.join(os.environ["BUILD_DIR"], "py", "dist"),
    # entry_points = {
    #     "console_scripts": [
    #         "scr-from-sac = cenote.util.scr_from_sac:main",
    #         "sac-from-scr = cenote.util.sac_from_scr:main",
    #         "plot = cenote.util.plot:main",
    #         "mod = cenote.util.mod:main",
    #     ],
    # },
    # test_suite = "test",
)