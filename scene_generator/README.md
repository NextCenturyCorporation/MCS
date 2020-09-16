# Scene Generator

## Setup

### Install Requirements

```
pip3 install -r requirements.txt
```

### Goal Images

The interactive scenes save the pixel array of each target object in each output JSON file by reading the images from the `images` folder. **You can run the scene generator without the images for internal testing.*** However, for generating new training and evaluation datasets, you must first run the `image_generator` to populate the `images` folder with each object/material combination pixel array text file (or download the files from S3). See the `image_generator` folder for more information.

Pixels (for the scene generator):

https://mcs-unity-images.s3.amazonaws.com/mcs-evaluation-pixels-summer-2020.tar.gz

Untar this file so it populates a folder called `images` inside this folder (`scene_generator`).

Images (for viewing):

https://mcs-unity-images.s3.amazonaws.com/mcs-evaluation-images-summer-2020.tar.gz

## Running

To see all of the scene generator's options:

```
python3 scene_generator.py
```

To generate 10 "Retrieval" training scenes with a file name prefix of "my_retrieval":

```
python3 scene_generator.py -p my_retrieval -c 10 -t Retrieval --training
```

To generate 20 "ObjectPermanence" evaluation quartets with a file name prefix of "eval_3":

```
python3 scene_generator.py -p eval_3 -c 20 -t ObjectPermanence
```

## Testing

Please note that the tests will take a few minutes to run!

```
python3 -m pytest --debug -v *_test.py -vv
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
