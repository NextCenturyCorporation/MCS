#!/bin/bash

cd python_api/machine_common_sense
python3 must_generate_sphinx_docs.py
status=$?
if [ $status -eq 1 ]
then
    exit $status
elif [ $status -eq 2 ]
then
    exit 0
fi
source sphinx_venv/bin/activate
cd docs
make markdown
cp _build/markdown/index.md ../../API.md
git add ../../API.md
echo "Finished update to Python API sphinx markdown documentation."

