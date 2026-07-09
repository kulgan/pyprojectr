from importlib.metadata import distribution

from pyprojectr import pyproject
from pyprojectr.core import BaseModel, PyProjectTool
from pyprojectr.pyproject import Author, BuildSystem, License, Maintainer, PyProject, PyProjectFile, Readme

VERSION = distribution(__name__).version

__all__ = [
    "VERSION",
    "Author",
    "BaseModel",
    "BuildSystem",
    "License",
    "Maintainer",
    "PyProject",
    "PyProjectFile",
    "PyProjectTool",
    "Readme",
    "pyproject",
]
