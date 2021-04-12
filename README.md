# MCS Python Package

- [Installation](#installation)
- [Download](#download)
- [Training Datasets](#training-datasets)
- [Usage](#usage)
- [Run with Human Input](#run-with-human-input)
- [Run with Scene Timer](#run-with-scene-timer)
- [Config File](#config-file)
- [Running Remotely](#running-remotely)
- [Containerization](#containerization)
- [Documentation](#documentation)
- [Other MCS GitHub Repositories](#other-mcs-github-repositories)
- [Troubleshooting/Email](#troubleshooting)
- [License](#apache-2-open-source-license)

## Installation

The latest release of the MCS Python library is `0.4.1.1`.

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

With the activated virtual environment, install the MCS package from the git url. MCS has a dependency on an ai2thor fork and will take a while to install. Please be patient.

```bash
(venv) $ python -m pip install git+https://github.com/NextCenturyCorporation/MCS@master#egg=machine_common_sense
```

## MCS Package Developer Installation

For MCS package developer, follow these [alternate instructions](./machine_common_sense/DEV.md)

## Download

Here are the instructions for downloading and installing our latest Unity release. For our previous releases, please see [this page](https://github.com/NextCenturyCorporation/MCS/releases).

### Unity Application

The latest release of the MCS Unity app is `0.4.1.1`.

Please note that our Unity App is built on Linux or Mac.

Linux Version:

1. [Download the latest MCS Unity App](https://github.com/NextCenturyCorporation/MCS/releases/download/0.4.1-1/MCS-AI2-THOR-Unity-App-v0.4.1.1.x86_64)

2. [Download the latest MCS Unity Data Directory TAR](https://github.com/NextCenturyCorporation/MCS/releases/download/0.4.1-1/MCS-AI2-THOR-Unity-App-v0.4.1.1_Data.tar.gz)

3. [Download the latest UnityPlayer.so file](https://github.com/NextCenturyCorporation/MCS/releases/download/0.4.1-1/UnityPlayer.so)

4. Ensure that both the Unity App and the TAR are in the same directory.

5. Untar the Data Directory:

```
tar -xzvf MCS-AI2-THOR-Unity-App-v0.4.1.1_Data.tar.gz
```

6. Mark the Unity App as executable:

```
chmod a+x MCS-AI2-THOR-Unity-App-v0.4.1.1.x86_64
```

Mac Version:

[Download the Mac ZIP](https://github.com/NextCenturyCorporation/MCS/releases/download/0.4.1-1/MCS-AI2-THOR-Unity-App-v0.4.1.1-mac.zip)


## Training Datasets

### Summer 2020

#### Passive Agent

Subtasks:

- Single object scenes (~10K), just like Eval 3
- Object preference scenes (~10K), just like Eval 3
- Multiple agents scenes (4K), new to Eval 4
- Instrumental action scenes (4K), new to Eval 4

JSON scene configuration files:

- https://eval-4-data.s3.amazonaws.com/eval_4_agent_training_dataset.zip

Rendered videos:

- https://nyu-datasets.s3.amazonaws.com/agent_instrumental_action_training_videos.zip
- https://nyu-datasets.s3.amazonaws.com/agent_multiple_agents_training_videos.zip
- https://nyu-datasets.s3.amazonaws.com/agent_object_preference_training_videos.zip
- https://nyu-datasets.s3.amazonaws.com/agent_single_object_training_videos.zip

#### Passive Intuitive Physics

Please generate your own training datasets using our Scene Generator software here:

- https://github.com/NextCenturyCorporation/mcs-scene-generator

#### Interactive

For the container, obstacle, and occluder tasks, please generate your own training datasets using our Scene Generator software here:

- https://github.com/NextCenturyCorporation/mcs-scene-generator

For the new interactive object permanence and reorientation tasks, please generate your own training datasets using our example scene templates here:

https://github.com/NextCenturyCorporation/MCS/tree/master/machine_common_sense/scenes#interactive-object-permanence-and-reorientation-tasks

### Winter 2020

*Please use the most recent 0.3.X release version*

Passive Agent (only expected scenes):
- https://evaluation-training-scenes.s3.amazonaws.com/eval3/training-single-object.zip
- https://evaluation-training-scenes.s3.amazonaws.com/eval3/training-object-preference.zip

Passive Intuitive Physics (only plausible scenes):
- https://evaluation-training-scenes.s3.amazonaws.com/eval3/training-passive-physics.zip

Example Scenes:
- https://github.com/NextCenturyCorporation/MCS/tree/master/machine_common_sense/scenes

### Summer 2020

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
controller = mcs.create_controller(unity_app_file_path, config_file_path='./some-path/config.ini')

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
controller = mcs.create_controller(unity_app_file_path)

for scene_json_file_path in scene_json_file_list:
    scene_data, status = mcs.load_scene_json_file(scene_json_file_path)
    output = controller.start_scene(scene_data)
    action, params = select_action(output)
    while action != '':
        controller.step(action, params)
            action, params = select_action(output)
    controller.end_scene()
```

Example with terminal logging:
```python
import logging
import machine_common_sense as mcs

logger = logging.getLogger('machine_common_sense')
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)

controller = mcs.create_controller(unity_app_file_path, config_file_path='./some-path/config.ini')
scene_data, status = mcs.load_scene_json_file(scene_json_file_path)
output = controller.start_scene(scene_data)

action, params = select_action(output)
while action != '':
    logger.debug(f"Taking {action} with {params{")
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
- `--config_file_path <file_path>`

## Run with Scene Timer

To run the Unity application and measure your runtime speed, you can run the `run_scene_timer` script that was installed in the package with the MCS Python Library:

```
run_scene_timer <mcs_unity_build_file> <mcs_scene_file_folder>
```

This will run all of the MCS scene configuration JSON files in the given folder, use the PASS action for 20 steps (or for a number of steps equal to the last_step of the scene file's goal, if any) in each scene, and print out the total, average, minimum, and maximum run time for all the scenes and the steps.

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

Otherwise, return the metadata for the visible and held objects.

#### noise_enabled

(boolean, optional)

Whether to add random noise to the numerical amounts in movement and object interaction action parameters. Will default to `False`.

#### seed

(int, optional)

A seed for the Python random number generator (defaults to None).

#### size

(int, optional)

Desired screen width. If value given, it must be more than `450`. If none given, screen width will default to `600`.

#### video_enabled

(boolean, optional)

Save videos of the RGB frames, depth masks, object instance segmentation masks (if returned in the output by the chosen metadata tier), 2D top-down scene views, and the heatmap images given to us in `make_step_prediction` by the AI performer.

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

### Example Scene Configuration Files

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

### Remote Run Test Script

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

## Containerization

### GPU Image
Please note that the GPU image requires an Nvidia GPU and Nvidia Docker to be installed.

You can run the GPU image with:
```shell
docker run -it -e PYTHONIOENCODING=utf8 -e XAUTHORITY=/tmp/.docker.xauth -e DISPLAY=:1 \
           -v ${PWD}/machine_common_sense/scenes:/input -v ${PWD}/scripts:/scripts \
           -v /tmp/.X11-unix:/tmp/.X11-unix \
           -v /tmp/.docker.xauth:/tmp/.docker.xauth \
           --net host --gpus all --rm mcs-playroom:0.0.6 bash
```

You can then run a scene like this:
```shell
python3 /scripts/run_human_input.py /mcs/MCS-AI2-THOR-Unity-App-v0.4.0.x86_64 --config_file_path /scripts/config_oracle.ini /input/hinged_container_example.json
```

#### Missing X Authorization Error
If you encounter an error like the following:
```
config_file_path $MCS_CONFIG_FILE_PATH /input/agents_preference_expected.json 
No protocol specified
xdpyinfo:  unable to open display ":1".
Exception in create_controller() Invalid DISPLAY :1 - cannot find X server with xdpyinf
```
please try resetting your X authorization:
```shell
sudo rmdir /tmp/.docker.xauth
touch /tmp/.docker.xauth
xauth nlist $DISPLAY | sed -e 's/^..../ffff/' | xauth -f /tmp/.docker.xauth nmerge -
```

### CPU Image

There is an image to run CPU-only without requiring an Nvidia GPU. Please only use it if your system does not meet the
prerequisites for the GPU image, since GPU acceleration will yield significantly better performance.

#### Build Image
```shell
docker build -f CPU_Container.dockerfile -t mcs-playroom-cpu .
```

#### Run Image (bash)
```shell
docker run -it -p 5900:5900 -v ${PWD}/machine_common_sense/scenes:/input -v ${PWD}/scripts:/scripts mcs-playroom-cpu bash
```

#### Run with VNC
Unless stated otherwise, the following commands are intended to be run inside the container.
Run tmux with `tmux` and open two panes via `C-b %`.
```shell
Xvnc :33 &
export DISPLAY=:33
python3 /scripts/run_human_input.py ${MCS_EXECUTABLE_PATH} --config_file_path ${MCS_CONFIG_FILE_PATH} /input/hinged_container_example.json
```

Switch panes with `C-b <arrow>`
```shell
window_id=$(xwininfo -root -tree | grep MCS-AI2-THOR | tail -n1 | sed "s/^[ \t]*//" | cut -d ' ' -f1) && echo ${window_id}
x11vnc -id ${window_id} &
```

Afterwards, you should be able to connect to the VNC server from the host by running `vncviewer` and connecting to
`localhost:5900`.

#### Run Fully Headless

As an alternative for batch runs you can also run MCS against X virtual framebuffers. In this case you do not get visual
output, but can run the images on headless servers without X server. To do so, please execute the following command
from inside the container:

```shell
xvfb-run -s "-screen 0 1440x900x24" python3 /scripts/run_human_input.py ${MCS_EXECUTABLE_PATH} --config_file_path ${MCS_CONFIG_FILE_PATH} /input/agents_preference_expected.json
```

## Documentation

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
