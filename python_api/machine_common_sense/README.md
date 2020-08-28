# MCS Python Library: Development README

- AI2-THOR Documentation: http://ai2thor.allenai.org/documentation
- AI2-THOR GitHub: https://github.com/allenai/ai2thor
- MCS AI2-THOR GitHub Fork: https://github.com/NextCenturyCorporation/ai2thor
- MCS AI2-THOR Scene Files and API: [scenes](./machine_common_sense/scenes)

## Setup

1. Build the MCS Unity application using the MCS fork of the AI2-THOR GitHub repository. On Linux, this will create the file `<cloned_repository>/unity/MCS-AI2-THOR.x86_64`. On Mac, it will look something like this: `<cloned_repository>/unity/<nameofbuild>.app/Contents/MacOS/<nameofbuild>`

2. Install the Python dependencies (I tested on Python v3.6.5)

```
pip install -r ../requirements.txt
```

3. Run pre-commit install to set up git hook

```
pre-commit install
```


## Running

We have made multiple run scripts:

- `run_mcs_environment.py` (random development testing)
- `run_mcs_human_input.py` (human input mode)
- `run_mcs_inphys_samples.py` (IntPhys sample scenes)
- `run_mcs_just_pass.py` (just pass repeatedly)
- `run_mcs_just_rotate.py` (rotate in a full circle, then exit)

To run a script from the terminal with visual output:

```
python3 run_mcs_environment.py <mcs_unity_build_file> <mcs_config_json_file>
```

To run it headlessly, first install xvfb (on Ubuntu, run `sudo apt-get install xvfb`), then:

```
xvfb-run --auto-servernum --server-args='-screen 0 640x480x24' python3 run_mcs_environment.py <mcs_unity_build_file> <mcs_config_json_file>
```

Each run will generate a subdirectory (named based on your config file) containing the output image files from each step.

## Running Local Code Changes

For development, install the `machine_common_sense` library using `pip` with the `-e` flag so it sees all of your local code changes.

```
cd <mcs_root_folder>
pip install -e .
```

## Logs

Looking for the logs from your Unity run? I found mine here: `~/.config/unity3d/CACI\ with\ the\ Allen\ Institute\ for\ Artificial\ Intelligence/MCS-AI2-THOR/Player.log` If using a Mac, Unity logs can be accessed from within the Console app here: `~/Library/Logs/Unity`

## Testing

See [../test/README.md](../test/README.md)

## Packaging

Packaging the project is done with the [setup.py](../../setup.py) file located in the root of this GitHub repository. See the [Python documentation](https://packaging.python.org/tutorials/packaging-projects/) for information.

## Documentation Style Guide

See https://numpydoc.readthedocs.io/en/latest/format.html

## Linting

We are currently using [flake8](https://flake8.pycqa.org/en/latest/) and [autopep8](https://pypi.org/project/autopep8/) for linting and formatting our Python code. This is only enforced within the python_api project for now. Both are [PEP 8](https://www.python.org/dev/peps/pep-0008/) compliant, although we are ignoring the following rules:
- **E402**: Module level import not at top of file
- **W504**: Line break occurred after a binary operator

A full list of error codes and warnings enforced can be found [here](https://flake8.pycqa.org/en/latest/user/error-codes.html)

Both have settings so that they should run on save within Visual Studio Code [settings.json](../.vscode/settings.json) as well as on commit after running `pre-commit install` (see [.pre-commit-config.yaml](../../.pre-commit-config.yaml) and [.flake8](../../.flake8)), but can also be run on the command line:


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

## Making GIFs

First, install ffmpeg. Then (change the frame rate with the `-r` option):

```
ffmpeg -r 3 -i frame_image_%d.png output.gif
```

## Sphinx Documentation

- Good Sphinx Tutorial: https://medium.com/@richdayandnight/a-simple-tutorial-on-how-to-document-your-python-project-using-sphinx-and-rinohtype-177c22a15b5b
- Markdown Builder: https://pypi.org/project/sphinx-markdown-builder/

- Sphinx: https://www.sphinx-doc.org/en/master/
- Sphinx's own Tutorial: https://www.sphinx-doc.org/en/master/usage/quickstart.html

## Setup

1. Install Python virtual environment: `pip3 install virtualenv` OR `sudo apt-get install python3-venv`
2. Switch to the python_api folder: `cd <mcs>/python_api/machine_common_sense/`
3. Create a virtual environment: `python3 -m venv venv`
4. Activate the virtual environment: `source venv/bin/activate`
5. Update pip: `pip3 install --upgrade pip setuptools wheel`
6. Install the MCS Python library: `cd ..; pip install -e .; cd python_api`
7. Install other dependencies: `pip install -r machine_common_sense/requirements.txt`
8. Enter the docs folder: `cd docs`
9. Generate the markdown docs in the build folder: `make markdown` (or the HTML docs: `make html`)
10. Finally, to exit your virtual environment: `deactivate`

