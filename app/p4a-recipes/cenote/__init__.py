from pythonforandroid.recipe import IncludedFilesBehaviour, PythonRecipe

class CenoteRecipe(IncludedFilesBehaviour, PythonRecipe):
    name = "cenote"
    src_filename = "../../../lib"
    depends = [
        # "pyyaml",
        "pint",
        # "ipdb",
        # "ipython",
        "dipplanner",
        "setuptools",
    ]
    call_hostpython_via_targetpython = False

recipe = CenoteRecipe()
