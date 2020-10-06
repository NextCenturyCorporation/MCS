#!/bin/bash

echo "calling python generate"
venv/bin/python scripts/generate_sphinx_docs.py
status=$?
echo $status
if [ $status -eq 1 ]
then
    exit $status
elif [ $status -eq 2 ]
then
    exit 0
fi
echo "moving to docs"
cd docs/
echo "calling make'"
make markdown
echo "moving to API"
cp _build/markdown/index.md ../machine_common_sense/API.md
git add ../machine_common_sense/API.md
echo "Finished update to Python API sphinx markdown documentation."
