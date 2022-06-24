from pythonforandroid.recipe import PythonRecipe

class DipplannerRecipe(PythonRecipe):
    version = "master"
    url = "https://github.com/ThomasChiroux/dipplanner/archive/master.zip"
    depends = [
        "setuptools",
    ]
    call_hostpython_via_targetpython = False

recipe = DipplannerRecipe()
