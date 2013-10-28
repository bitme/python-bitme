#!/bin/bash
IDENTITY=46C171A0
python setup.py bdist_egg upload --sign --identity=$IDENTITY
python setup.py sdist upload --sign --identity=$IDENTITY
