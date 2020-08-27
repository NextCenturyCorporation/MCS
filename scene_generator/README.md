# Scene Generator

## Setup

### Install Requirements

```
pip3 install -r requirements.txt
```

### Goal Images

If you want to have an image pixel array for each target object in the interactive goals, you must first run the `image_generator` to populate the `images` folder with each object/material combination pixel array text file (or download the files from S3).

Pixels (for the scene generator):

https://mcs-unity-images.s3.amazonaws.com/mcs-evaluation-pixels-summer-2020.tar.gz

Untar this file so it populates a folder called `images` inside this folder (`scene_generator`).

Images (for viewing):

https://mcs-unity-images.s3.amazonaws.com/mcs-evaluation-images-summer-2020.tar.gz

## Running

The following will show the script's options in your terminal:

```
python3 scene_generator.py
```

Here's an example that generates 10 retrieval scenes:

```
python3 scene_generator.py --prefix my_scene -c 10 --goal Retrieval --find_path
```

## Testing

Please note that the tests will take a few minutes to run!

```
python3 -m pytest *_test.py
```

## Linting

We are currently using [flake8](https://flake8.pycqa.org/en/latest/) and [autopep8](https://pypi.org/project/autopep8/) for linting and formatting our Python code. This is enforced within the python_api and scene_generator projects. Both are [PEP 8](https://www.python.org/dev/peps/pep-0008/) compliant (besides some inline exceptions), although we are ignoring the following rules:
- **E402**: Module level import not at top of file
- **W504**: Line break occurred after a binary operator

A full list of error codes and warnings enforced can be found [here](https://flake8.pycqa.org/en/latest/user/error-codes.html)

Both have settings so that they should run on save within Visual Studio Code [settings.json](../.vscode/settings.json) as well as on commit after running `pre-commit install` (see [.pre-commit-config.yaml](../../.pre-commit-config.yaml) and [.flake8](../../.flake8)), but can also be run on the command line:


```
flake8 --per-file-ignores="materials.py:E501"
```

and

```
autopep8 --in-place --aggressive --recursive <directory>
```
or
```
autopep8 --in-place --aggressive <file>
```
