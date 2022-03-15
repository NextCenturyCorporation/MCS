#!/bin/bash

echo "calling python generate"
venv/bin/python docs/generate_sphinx_docs.py
status=$?
echo $status
if [ $status -eq 1 ]
then
    exit $status
elif [ $status -eq 2 ]
then
    exit 0
fi
echo "calling make"
make html
echo "Finished update to Python API sphinx html documentation."
