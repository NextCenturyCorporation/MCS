# MCS Sphinx Documentation

- Good Sphinx Tutorial: https://medium.com/@richdayandnight/a-simple-tutorial-on-how-to-document-your-python-project-using-sphinx-and-rinohtype-177c22a15b5b
- Markdown Builder: https://pypi.org/project/sphinx-markdown-builder/

- Sphinx: https://www.sphinx-doc.org/en/master/
- Sphinx's own Tutorial: https://www.sphinx-doc.org/en/master/usage/quickstart.html

## Setup

1. Install Python virtual environment: `sudo apt-get install python3-venv`
2. Switch to the python_api folder: `cd <mcs>/python_api`
3. Create a virtual environment: `python3 -m venv sphinx_venv`
4. Activate the virtual environment: `source sphinx_venv/bin/activate`
5. Update pip: `pip3 install --upgrade pip setuptools wheel`
6. Install the MCS Python library: `cd ..; pip install -e .; cd python_api`
7. Install other dependencies: `pip install -r machine_common_sense/requirements.txt`
8. Enter the docs folder: `cd docs`
9. Generate the markdown docs in the build folder: `make markdown` (or the HTML docs: `make html`)
10. Finally, to exit your virtual environment: `deactivate`

Note that you may see the following warning: `WARNING: The config value `source_suffix' has type `dict', defaults to `list'.`
