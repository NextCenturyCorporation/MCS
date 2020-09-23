# MCS Package Developer

## Package Installation

### Create a Virtual Environment

```
$ python3.6 -m venv --prompt mcs venv
$ source venv/bin/activate
(mcs) $ python -m pip install --upgrade pip setuptools wheel
```

### Install the MCS Package and dependencies

From the MCS root folder, install the package in your virtual environment in editable mode (-e) so that local changes will automatically reflect in the virtual environment.

```
python -m pip install -e .
```

Additionally, install the packages included in the requirements file so that linting and documentation work. The requirements.txt file includes developer dependencies.

```
python -m pip install -r requirements.txt
```

### Run pre-commit

Run pre-commit install to set up the git hooks for linting and auto-documentation.

```
pre-commit install
```

## Linting

We are currently using [flake8](https://flake8.pycqa.org/en/latest/) and [autopep8](https://pypi.org/project/autopep8/) for linting and formatting our Python code. This is enforced within the python_api and scene_generator projects. Both are [PEP 8](https://www.python.org/dev/peps/pep-0008/) compliant (besides some inline exceptions), although we are ignoring the following rules:
- **E402**: Module level import not at top of file
- **W504**: Line break occurred after a binary operator

A full list of error codes and warnings enforced can be found [here](https://flake8.pycqa.org/en/latest/user/error-codes.html)

Both have settings so that they should run on save within Visual Studio Code [settings.json](.vscode/settings.json) as well as on commit after running `pre-commit install` (see [.pre-commit-config.yaml](.pre-commit-config.yaml) and [.flake8](.flake8)), but can also be run on the command line:


```
flake8
```

and

```
autopep8 --in-place --aggressive --recursive <directory>
```
or
```
autopep8 --in-place --aggressive <file>
```

## Sphinx Documentation

- Good Sphinx Tutorial: https://medium.com/@richdayandnight/a-simple-tutorial-on-how-to-document-your-python-project-using-sphinx-and-rinohtype-177c22a15b5b
- Markdown Builder: https://pypi.org/project/sphinx-markdown-builder/

- Sphinx: https://www.sphinx-doc.org/en/master/
- Sphinx's own Tutorial: https://www.sphinx-doc.org/en/master/usage/quickstart.html

## Python Style Guide

See https://numpydoc.readthedocs.io/en/latest/format.html

## Running

We have made multiple run scripts:

To run a script (like `run_human_input.py`) from the terminal with visual output:

```
run_human_input <mcs_unity_build_file> <mcs_config_json_file>
```

To run it headlessly, first install xvfb (on Ubuntu, run `sudo apt-get install xvfb`), then:

```
xvfb-run --auto-servernum --server-args='-screen 0 640x480x24' python3 run_human_input.py <mcs_unity_build_file> <mcs_config_json_file>
```

Each run will generate a subdirectory (named based on your config file) containing the output image files from each step.

## Making GIFs

First, install ffmpeg. Then (change the frame rate with the `-r` option):

```
ffmpeg -r 3 -i frame_image_%d.png output.gif
```

## References

- AI2-THOR Documentation: http://ai2thor.allenai.org/documentation
- AI2-THOR GitHub: https://github.com/allenai/ai2thor
- MCS AI2-THOR GitHub Fork: https://github.com/NextCenturyCorporation/ai2thor
- MCS AI2-THOR Scene Files and API: [scenes](./machine_common_sense/scenes)
- 