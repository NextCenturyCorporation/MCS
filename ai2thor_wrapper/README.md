# MCS AI2-THOR Python Wrapper

- AI2-THOR Documentation:  http://ai2thor.allenai.org/documentation
- AI2-THOR GitHub:  https://github.com/allenai/ai2thor
- MCS AI2-THOR GitHub Fork:  https://github.com/NextCenturyCorporation/ai2thor
- MCS AI2-THOR Scene Files and API:  [scenes](./scenes)

## Setup

1. Build the MCS Unity application using the MCS fork of the AI2-THOR GitHub repository.  On Linux, this will create the file `<cloned_repository>/unity/MCS-AI2-THOR.x86_64`. On Mac, it will look something like this: `<cloned_repository>/unity/<nameofbuild>.app/Contents/MacOS/<nameofbuild>`

2. Install the Python dependencies (I tested on Python v3.6.5)

```
pip install ai2thor
pip install Pillow
```

## Run

To run via command line with visual output (note that on a Mac, the command would be "python3" instead of "python"):

```
python run_mcs_environment.py <mcs_unity_build_file> <mcs_config_json_file>
```

To run via command line headlessly, first install xvfb (on Ubuntu, run `sudo apt-get install xvfb`), then:

```
xvfb-run --auto-servernum --server-args='-screen 0 640x480x24' python run_mcs_environment.py <mcs_unity_build_file> <mcs_config_json_file>
```

Each run will generate a subdirectory (named based on your config file) containing the output image files from each step.

Looking for the logs from your Unity run?  I found mine here:  `~/.config/unity3d/CACI\ with\ the\ Allen\ Institute\ for\ Artificial\ Intelligence/MCS-AI2-THOR/Player.log` If using a Mac, Unity logs can be accessed from within the Console app here: `~/Library/Logs/Unity`

## Test

```
python -m unittest
```

## Documentation Style Guide

See https://numpydoc.readthedocs.io/en/latest/format.html

