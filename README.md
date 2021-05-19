# MCS Python Package

- [Installation](#installation)
- [Download](#download)
- [Usage](#usage)
- [Config File](#config-file)
- [Documentation](#documentation)
- [Other MCS GitHub Repositories](#other-mcs-github-repositories)
- [Troubleshooting/Email](#troubleshooting)
- [License](#apache-2-open-source-license)

## Installation

The latest release of the MCS Python library is `0.4.3`.

### Virtual Environments

Python virtual environments are recommended when using the MCS package. All steps below presume the activation of the virtual environment as shown. These instructions are for Ubuntu linux.

The Machine Common Sense package has a requirement of Python 3.6 or greater.

#### Traditional Python Environment

```bash
$ python3.6 -m venv venv
$ source venv/bin/activate
(venv) $ python -m pip install --upgrade pip setuptools wheel
```

#### Anaconda Environment

From the base Anaconda environment, create your project virtual environment.

```bash
(base) $ conda create -n myenv python=3.8
(base) $ conda env list
# conda environments:
#
base                  *  /home/user/anaconda3
myenv                    /home/user/anaconda3/envs/myenv
(base) $ conda activate myenv
(myenv) $
```

### Install MCS

With the activated virtual environment, install the MCS package from the git url. MCS has a dependency on ai2thor and could take a while to install.

```bash
(venv) $ python -m pip install git+https://github.com/NextCenturyCorporation/MCS@master#egg=machine_common_sense
```

## Download

Here are the instructions for downloading and installing our latest Unity release. For our previous releases, please see [this page](https://github.com/NextCenturyCorporation/MCS/releases).

### Unity Application

The latest release of the MCS Unity app is `0.4.3`.

Please note that our Unity App is built for Linux or Mac. There is no Windows support currently.

Linux Version:

*Please note that the download links have changed as of version 0.4.3*

1. [Download and unzip the Linux ZIP](https://github.com/NextCenturyCorporation/MCS/releases/download/0.4.3/MCS-AI2-THOR-Unity-App-v0.4.3-linux.zip)

2. Ensure that the Unity App, the Data Directory TAR, and the UnityPlayer.so file are all in the same directory.

3. Untar the Data Directory:

```
tar -xzvf MCS-AI2-THOR-Unity-App-v0.4.3_Data.tar.gz
```

4. Mark the Unity App as executable:

```
chmod a+x MCS-AI2-THOR-Unity-App-v0.4.3.x86_64
```

Mac Version:

[Download the Mac ZIP](https://github.com/NextCenturyCorporation/MCS/releases/download/0.4.3/MCS-AI2-THOR-Unity-App-v0.4.3-mac.zip)

## Usage

Example usage of the MCS library:

```python
import machine_common_sense as mcs

# Unity app file will be downloaded automatically
controller = mcs.create_controller(config_file_path='./some-path/config.ini')

# Either load the scene data dict from an MCS scene config JSON file or create your own.
# We will give you the training scene config JSON files and the format to make your own.
scene_data, status = mcs.load_scene_json_file(scene_json_file_path)

output = controller.start_scene(scene_data)

# Use your machine learning algorithm to select your next action based on the scene
# output (goal, actions, images, metadata, etc.) from your previous action.
action, params = select_action(output)

# Continue to select actions until your algorithm decides to stop.
while action != '':
    controller.step(action, params)
    action, params = select_action(output)

# For interaction-based goals, your series of selected actions will be scored.
# For observation-based goals, you will pass a classification and a confidence
# to the end_scene function here.
controller.end_scene()
```

## Config File

To use an MCS configuration file, you can either pass in a file path via the `config_file_path` property in the create_controller() method, or set the `MCS_CONFIG_FILE_PATH` environment variable to the path of your MCS configuration file (note that the configuration must be an INI file -- see [sample_config.ini](./sample_config.ini) for an example).

### Config File Properties

#### history_enabled

(boolean, optional)

Whether to save the scene history output data in your local directory. Default: True

#### metadata

(string, optional)

The `metadata` property describes what metadata will be returned by the MCS Python library. The `metadata` property is available so that users can run baseline or ablation studies during training. It can be set to one of the following strings:

- `oracle`: Returns the metadata for all the objects in the scene, including visible, held, and hidden objects. Object masks will have consistent colors throughout all steps for a scene.
- `level2`: Only returns the images (with depth maps AND object masks), camera info, and properties corresponding to the player themself (like head tilt or pose). No information about specific objects will be included. Note that here, object masks will have randomized colors per step.
- `level1`: Only returns the images (with depth maps but NOT object masks), camera info, and properties corresponding to the player themself (like head tilt or pose). No information about specific objects will be included.
- `none`: Only returns the images (but no depth maps or object masks), camera info, and properties corresponding to the player themself (like head tilt or pose). No information about specific objects will be included.

If no metadata level is set:
- `default`: Fallback if no metadata level is specified. Only meant for use during development (evaluations will never be run this way). Includes metadata for visible and held objects in the scene, as well as camera info and properties corresponding to the player. Does not include depth maps or object masks.

#### noise_enabled

(boolean, optional)

Whether to add random noise to the numerical amounts in movement and object interaction action parameters. Will default to `False`.

#### save_debug_images

(boolean, optional)

Save RGB frames, depth masks, and object instance segmentation masks (if returned in the output by the chosen metadata tier) to image files on each step. Default: False

#### save_debug_json

(boolean, optional)

Save AI2-THOR/Unity input, AI2-THOR/Unity output, and MCS StepMetadata output to JSON file on each step. Default: False

#### seed

(int, optional)

A seed for the Python random number generator (defaults to None).

#### size

(int, optional)

Desired screen width. If value given, it must be more than `450`. If none given, screen width will default to `600`.

#### video_enabled

(boolean, optional)

Create and save videos of the RGB frames, depth masks, object instance segmentation masks (if returned in the output by the chosen metadata tier), 2D top-down scene views, and the heatmap images given to us in `make_step_prediction` by the AI performer. Default: False

### Using the Config File to Generate Scene Graphs or Maps

1. Save your .ini MCS configuration file with:
```
[MCS]
metadata: oracle`
```

2. Create a simple Python script to loop over one or more JSON scene configuration files, load each scene in the MCS controller, and save the output data in your own scene graph or scene map format.

```python
import os
import machine_common_sense as mcs

os.environ['MCS_CONFIG_FILE_PATH'] = # Path to your MCS configuration file

scene_files = # List of scene configuration file paths

controller = mcs.create_controller()

for scene_file in scene_files:
    scene_data, status = mcs.load_scene_json_file(scene_file)

    if status is not None:
        print(status)
    else:
        output = controller.start_scene(scene_data)
        # Use the output to save your scene graph or map
```

## Documentation

<!-- TODO where are sphinx docs published? -->
- [Python API](./machine_common_sense/API.md)
- [Example Scene Configuration Files](./machine_common_sense/scenes/README.md)
- [Scene Configuration JSON Schema](./machine_common_sense/scenes/SCHEMA.md)
- [Developer Docs](./machine_common_sense/DEV.md)

## Other MCS GitHub Repositories

- [Unity code](https://github.com/NextCenturyCorporation/ai2thor)
- [Scene Generator](https://github.com/NextCenturyCorporation/mcs-scene-generator)
- [Data Ingest](https://github.com/NextCenturyCorporation/mcs-ingest)
- [Evaluation Dashboard (UI)](https://github.com/NextCenturyCorporation/mcs-ui)

## Troubleshooting

[mcs-ta2@machinecommonsense.com](mailto:mcs-ta2@machinecommonsense.com)

## Apache 2 Open Source License

Code in this repository is made available by [CACI][4] (formerly [Next Century
Corporation][1]) under the [Apache 2 Open Source License][2].  You may
freely download, use, and modify, in whole or in part, the source code
or release packages. Any restrictions or attribution requirements are
spelled out in the license file.  For more information about the
Apache license, please visit the [The Apache Software Foundation’s
License FAQ][3].

[1]: http://www.nextcentury.com
[2]: http://www.apache.org/licenses/LICENSE-2.0.txt
[3]: http://www.apache.org/foundation/license-faq.html
[4]: http://www.caci.com

Copyright 2021 CACI (formerly Next Century Corporation)
