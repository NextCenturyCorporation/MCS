# MCS Python Package

## Installation

The latest release of the MCS Python library is `0.3.3`.

### Virtual Environments

Python virtual environments are recommended when using the MCS package. All steps below presume the activation of the virtual environment as shown.

```
python3.6 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
```

### Install MCS

With the activated virtual environment, install the MCS package from the git url. MCS has a dependency on an ai2thor fork and will take a while to install. Please be patient.

```
python -m pip install git+https://github.com/NextCenturyCorporation/MCS@latest#egg=machine_common_sense
```

## MCS Package Developer Installation

For MCS package developer, follow these alternate instructions.

[DEV.md](./machine_common_sense/DEV.md)

## Download

Here are the instructions for downloading and installing our latest Unity release. For our previous releases, please see [this page](https://github.com/NextCenturyCorporation/MCS/releases).

### Unity Application

The latest release of the MCS Unity app is `0.3.3`.

Please note that our Unity App is built on Linux. If you need a Mac or Windows version, please [contact us](#troubleshooting) directly.

1. [Download the Latest MCS Unity App](https://github.com/NextCenturyCorporation/MCS/releases/download/0.3.3/MCS-AI2-THOR-Unity-App-v0.3.3.x86_64)

2. [Download the Latest MCS Unity Data Directory TAR](https://github.com/NextCenturyCorporation/MCS/releases/download/0.3.3/MCS-AI2-THOR-Unity-App-v0.3.3_Data.tar.gz)

3. Ensure that both the Unity App and the TAR are in the same directory.

4. Untar the Data Directory:

```
tar -xzvf MCS-AI2-THOR-Unity-App-v0.3.3_Data.tar.gz
```

5. Mark the Unity App as executable:

```
chmod a+x MCS-AI2-THOR-Unity-App-v0.3.3.x86_64
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
controller = mcs.create_controller(unity_app_file_path, depth_maps=True,
                                   object_masks=True)

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

Example running multiple scenes sequentially:

```python
import machine_common_sense as mcs

# Only create the MCS controller ONCE!
controller = mcs.create_controller(unity_app_file_path, depth_maps=True,
                                   object_masks=True)

for scene_json_file_path in scene_json_file_list:
    scene_data, status = mcs.load_scene_json_file(scene_json_file_path)
    output = controller.start_scene(scene_data)
    action, params = select_action(output)
    while action != '':
        controller.step(action, params)
            action, params = select_action(output)
    controller.end_scene()
```

## Run with Human Input

To start the Unity application and enter your actions and parameters from the terminal, you can run the `run_in_human_input_mode` script that was installed in the package with the MCS Python Library (the `mcs_unity_build_file` is the Unity executable downloaded previously):

```
run_in_human_input_mode <mcs_unity_build_file> <mcs_scene_json_file>
```

Run options:
- `--depth_maps`
- `--object_masks`

## Run with Scene Timer

To run the Unity application and measure your runtime speed, you can run the `run_scene_timer` script that was installed in the package with the MCS Python Library:

```
run_scene_timer <mcs_unity_build_file> <mcs_scene_file_folder>
```

This will run all of the MCS scene configuration JSON files in the given folder, use the PASS action for 20 steps (or for a number of steps equal to the last_step of the scene file's goal, if any) in each scene, and print out the total, average, minimum, and maximum run time for all the scenes and the steps.

## Config File

To use an MCS configuration file, set the `MCS_CONFIG_FILE_PATH` environment variable to the path of your MCS configuration file (note that the configuration must be an INI file -- see [sample_config.ini](./sample_config.ini) for an example).

### Config File Properties

#### metadata

The `metadata` property describes what metadata will be returned by the MCS Python library. The `metadata` property is available so that users can run baseline or ablation studies during training. It can be set to one of the following strings:

- `oracle`: Returns the metadata for all the objects in the scene, including visible, held, and hidden objects. Object masks will have consistent colors throughout all steps for a scene.
- `level2`: Only returns the images (with depth masks AND object masks), camera info, and properties corresponding to the player themself (like head tilt or pose). No information about specific objects will be included. Note that here, object masks will have randomized colors per step.
- `level1`: Only returns the images (with depth masks but NOT object masks), camera info, and properties corresponding to the player themself (like head tilt or pose). No information about specific objects will be included.

Otherwise, return the metadata for the visible and held objects.

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

unity_app = # Path to your MCS Unity application

controller = mcs.create_controller(unity_app)

for scene_file in scene_files:
    scene_data, status = mcs.load_scene_json_file(scene_file)

    if status is not None:
        print(status)
    else:
        output = controller.start_scene(scene_data)
        # Use the output to save your scene graph or map
```

## Documentation

[API.md](./machine_common_sense/API.md)

## Example Scene Configuration Files

[machine_common_sense/scenes/README.md](./machine_common_sense/scenes/README.md)

## Running Remotely

To run MCS on a remote GPU server, use the following steps to launch an X11 server.

```bash
# query the gpu bus ID
$ nvidia-xconfig --query-gpu-info

GPU #0:
  Name      : Tesla K80
  UUID      : GPU-d03a3d49-0641-40c9-30f2-5c3e4bdad498
  PCI BusID : PCI:0:23:0
# create the xserver configuration
$ sudo nvidia-xconfig --user-display-device=None --virtual=600x400 --output-xconfig=/etx/X11/xorg.conf --busid=PCI:0:23:0
# launch Xserver
$ sudo /usr/bin/Xorg :0 &
# test using glxinfo
$ DISPLAY=:0 glxinfo
name of display: :0
display: :0  screen: 0
direct rendering: Yes
server glx vendor string: NVIDIA Corporation
server glx version string: 1.4

```

### Test script

Run the following script to test MCS with the X11 server created above.

```python
# test.py
import machine_common_sense as mcs
# use your path to the MCS Unity executable
controller = mcs.create_controller('MCS.x86_64')
# find a test scene
scene_file_path = 'playroom.json'
scene_data, status = mcs.load_scene_json_file(scene_file_path)
scene_file_name = scene_file_path[scene_file_path.rfind('/')+1]
if 'name' not in scene_data.keys():
    scene_data['name'] = scene_file_name[0:scene_file_name.find('.')]
output = controller.start_scene(scene_data)
for i in range(1, 12):
    output = controller.step('RotateLook')
    for j in range(len(output.image_list)):
        output.image_list[i].save(f'{i}-{j}.jpg')
```

From your python environment, run test.py and check the output images for proper rendering.

```
DISPLAY=:0 python test.py
```

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
