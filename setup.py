#Use by calling:
# python setup.py build_ext --inplace
#If you get "ImportError: No module named Cython.Distutils" then check if you have cython installed.
# pip install cython

from setuptools import setup
from setuptools import Extension
from Cython.Distutils import build_ext
import numpy

setup(
    cmdclass = {'build_ext': build_ext},
    ext_modules = [Extension("addDateNDVI", ["addDateNDVI.pyx"],
                             include_dirs=[numpy.get_include()]),
                   ],
)
