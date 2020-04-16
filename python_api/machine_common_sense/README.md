# MCS Python Library: Development README

- AI2-THOR Documentation: http://ai2thor.allenai.org/documentation
- AI2-THOR GitHub: https://github.com/allenai/ai2thor
- MCS AI2-THOR GitHub Fork: https://github.com/NextCenturyCorporation/ai2thor
- MCS AI2-THOR Scene Files and API: [scenes](./machine_common_sense/scenes)

## Setup

1. Build the MCS Unity application using the MCS fork of the AI2-THOR GitHub repository. On Linux, this will create the file `<cloned_repository>/unity/MCS-AI2-THOR.x86_64`. On Mac, it will look something like this: `<cloned_repository>/unity/<nameofbuild>.app/Contents/MacOS/<nameofbuild>`

2. Install the Python dependencies (I tested on Python v3.6.5)

```
pip install ai2thor
pip install Pillow
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

## Making GIFs

First, install ffmpeg. Then (change the frame rate with the `-r` option):

```
ffmpeg -r 3 -i frame_image_%d.png output.gif
```

