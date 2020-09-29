# MCS Python Package

## Installation

The latest release of the MCS Python library is `0.1.0`.

### Virtual Environments

Python virtual environments are recommend when using the MCS package. All steps presume the activation of the virtual environment as shown below.

```
python3.6 -m venv --prompt mcs venv
source venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
```

### Install MCS

With the activated virtual environment, install the MCS package from the git url. MCS has a dependency on an ai2thor fork and will take a while to install. Please be patient.

```
python -m pip install git+https://github.com/NextCenturyCorporation/MCS@latest
```

## MCS Package Developer Installation

For MCS package developer, follow these instructions.

[DEV.md](./machine_common_sense/DEV.md)

## Download

Here are the instructions for downloading and installing our latest Unity release. For our previous releases, please see [this page](https://github.com/NextCenturyCorporation/MCS/releases).

### Unity Application

The latest release of the MCS Unity app is `0.1.0`.

Please note that our Unity App is built on Linux. If you need a Mac or Windows version, please [contact us](#troubleshooting) directly.

1. [Download the Latest MCS Unity App](https://github.com/NextCenturyCorporation/MCS/releases/download/0.1.0/MCS-AI2-THOR-Unity-App-v0.1.0.x86_64)

2. [Download the Latest MCS Unity Data Directory TAR](https://github.com/NextCenturyCorporation/MCS/releases/download/0.1.0/MCS-AI2-THOR-Unity-App-v0.1.0_Data.tar.gz)

3. Ensure that both the Unity App and the TAR are in the same directory.

4. Untar the Data Directory:

```
tar -xzvf MCS-AI2-THOR-Unity-App-v0.1.0_Data.tar.gz
```

5. Mark the Unity App as executable:

```
chmod a+x MCS-AI2-THOR-Unity-App-v0.1.0.x86_64
```

### Training Datasets

#### Summer 2020

*Use a release version between 0.0.9 and 0.1.0*

Interactive:
https://evaluation2-training-scenes.s3.amazonaws.com/interaction-scenes.zip

Passive IntPhys:
https://evaluation2-training-scenes.s3.amazonaws.com/intphys-scenes.zip

Passive IntPhys Validation Data:
https://evaluation2-training-scenes.s3.amazonaws.com/validation-intphys-scenes.zip

## Usage

Example usage of the MCS library:

```python
import machine_common_sense as mcs

# We will give you the Unity app file.
controller = mcs.create_controller(unity_app_file_path, depth_masks=True,
                                   object_masks=True)

# Either load the config data dict from an MCS config JSON file or create your own.
# We will give you the training config JSON files and the format to make your own.
config_data = mcs.load_config_json_file(config_json_file_path)

output = controller.start_scene(config_data)

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

Example running multiple scenes sequentially:

```python
import machine_common_sense as mcs

# Only create the MCS controller ONCE!
controller = mcs.create_controller(unity_app_file_path, depth_masks=True,
                                   object_masks=True)

for config_json_file_path in config_json_file_list:
    config_data = mcs.load_config_json_file(config_json_file_path)
    output = controller.start_scene(config_data)
    action, params = select_action(output)
    while action != '':
        controller.step(action, params)
            action, params = select_action(output)
    controller.end_scene()
```

## Run with Human Input

To start the Unity application and enter your actions and parameters from the terminal, you can run the `run_in_human_input_mode` script that was installed in the package with the MCS Python Library (the `mcs_unity_build_file` is the Unity executable downloaded previously):

```
run_in_human_input_mode <mcs_unity_build_file> <mcs_config_json_file>
```

Run options:
- `--debug`
- `--depth_masks`
- `--noise`
- `--object_masks`
- `--seed <python_random_seed>`
- `--size <screen_width_450_or_more>`

## Run with Scene Timer

To run the Unity application and measure your runtime speed, you can run the `run_scene_timer` script that was installed in the package with the MCS Python Library:

```
run_scene_timer <mcs_unity_build_file> <mcs_config_file_folder>
```

Run options:
- `--debug`

This will run all of the MCS scene configuration JSON files in the given folder, use the PASS action for 20 steps (or for a number of steps equal to the last_step of the config file's goal, if any) in each scene, and print out the total, average, minimum, and maximum run time for all the scenes and the steps.

## Config File

To use an MCS configuration file, set the `MCS_CONFIG_FILE_PATH` environment variable to the path of your MCS configuration file.

### Config File Properties

#### metadata

The `metadata` property describes what metadata will be returned by the MCS Python library. The `metadata` property is available so that users can run baseline or ablation studies during training. It can be set to one of the following strings:

- `full`: Returns the metadata for all the objects in the scene, including visible, held, and hidden objects.
- `no_navigation`: Does not return the position or rotation of the player or the objects in the scene.
- `no_vision`: Does not return the depth or object masks, camera properties, or object dimensions, directions, or distances.
- `none`: Only returns the images (but not the masks), object IDs, and properties corresponding to the player themself (like head tilt or pose) and haptic feedback (like mass or materials of held objects).

Otherwise, return the metadata for the visible and held objects.

### Using the Config File to Generate Scene Graphs or Maps

1. Save your MCS configuration file with `metadata: full`

2. Create a simple Python script to loop over one or more JSON scene configuration files, load each scene in the MCS controller, and save the output data in your own scene graph or scene map format.

```python
import os
import machine_common_sense as mcs

os.environ['MCS_CONFIG_FILE_PATH'] = # Path to your MCS configuration file

scene_files = # List of scene configuration file paths

unity_app = # Path to your MCS Unity application

controller = mcs.create_controller(unity_app)

for scene_file in scene_files:
    config_data, status = mcs.load_config_json(scene_file)

    if status is not None:
        print(status)
    else:
        output = controller.start_scene(config_data)
        # Use the output to save your scene graph or map
```

## Documentation

[API.md](./machine_common_sense/API.md)

## Example Scene Configuration Files

[machine_common_sense/scenes/README.md](./machine_common_sense/scenes/SCENE_README.md)

## Troubleshooting

[mcs-ta2@machinecommonsense.com](mailto:mcs-ta2@machinecommonsense.com)

## Apache 2 Open Source License

Code in this repository is made available by [Next Century
Corporation][1] under the [Apache 2 Open Source License][2].  You may
freely download, use, and modify, in whole or in part, the source code
or release packages. Any restrictions or attribution requirements are
spelled out in the license file.  For more information about the
Apache license, please visit the [The Apache Software Foundation’s
License FAQ][3].

[1]: http://www.nextcentury.com
[2]: http://www.apache.org/licenses/LICENSE-2.0.txt
[3]: http://www.apache.org/foundation/license-faq.html
