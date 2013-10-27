import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "bitme",
    version = "0.0.1",
    author = "Erik Gregg",
    author_email = "ralree@gmail.com",
    description = ("Bitme bitcoin exchange API"),
    license = "MIT",
    keywords = "bitme bitcoin exchange api trade",
    url = "https://github.com/hank/bitme-python",
    packages=['bitme'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: MIT License",
    ],
)
