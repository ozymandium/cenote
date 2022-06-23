from pythonforandroid.recipe import IncludedFilesBehaviour, PythonRecipe

class CenoteRecipe(IncludedFilesBehaviour, PythonRecipe):
    name = "cenote"
    src_filename = "../../cenote"
    depends = [
        "pyyaml",
        "pint",
        "ipdb",
        "ipython",
        "matplotlib",
        "pytest",
        "coverage",
        "dipplanner",
    ]

recipe = CenoteRecipe()
