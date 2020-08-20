# MCS Python Library: Usage README

## Download

Here are the instructions for downloading and installing our latest Python and Unity release. For our previous releases, please see [this page](https://github.com/NextCenturyCorporation/MCS/releases).

### Python Library

The latest release of the MCS Python library is `0.0.10`. We will accept Evaluation 2 submissions with a minimum version of 0.0.9 given the short timeframe between this release and submission.

1. Install the required third-party Python libraries:

```
pip3 install -r requirements.txt
```

2. Ensure you've installed `ai2thor` version `2.2.0`:

```
pip3 show ai2thor
```

3. Install the MCS Python Library:

```
pip3 install git+https://github.com/NextCenturyCorporation/MCS@latest
```

### Unity Application

The latest release of the MCS Unity app is `0.0.10`.

Please note that our Unity App is built on Linux. If you need a Mac or Windows version, please [contact us](#troubleshooting) directly.

1. [Download the Latest MCS Unity App](https://github.com/NextCenturyCorporation/MCS/releases/download/0.0.10/MCS-AI2-THOR-Unity-App-v0.0.10.x86_64)

2. [Download the Latest MCS Unity Data Directory TAR](https://github.com/NextCenturyCorporation/MCS/releases/download/0.0.10/MCS-AI2-THOR-Unity-App-v0.0.10_Data.tar.gz)

3. Ensure that both the Unity App and the TAR are in the same directory.

4. Untar the Data Directory:

```
tar -xzvf MCS-AI2-THOR-Unity-App-v0.0.10_Data.tar.gz
```

5. Mark the Unity App as executable:

```
chmod a+x MCS-AI2-THOR-Unity-App-v0.0.10.x86_64
```

### Training Dataset

Interactive:
https://evaluation2-training-scenes.s3.amazonaws.com/interaction-scenes.zip

Intphys:
https://evaluation2-training-scenes.s3.amazonaws.com/intphys-scenes.zip

Intphys Validation Set:
https://evaluation2-training-scenes.s3.amazonaws.com/validation-intphys-scenes.zip

## Import

Example importing the MCS library:

```python
from machine_common_sense import MCS

# We will give you the Unity app file.
controller = MCS.create_controller(unity_app_file_path)

# Either load the config data dict from an MCS config JSON file or create your own.
# We will give you the training config JSON files and the format to make your own.
config_data = MCS.load_config_json_file(config_json_file_path)

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
from machine_common_sense import MCS

# Only create the MCS controller ONCE!
controller = MCS.create_controller(unity_app_file_path)

for config_json_file_path in config_json_file_list:
    config_data = MCS.load_config_json_file(config_json_file_path)
    output = controller.start_scene(config_data)
    action, params = select_action(output)
    while action != '':
        controller.step(action, params)
            action, params = select_action(output)
    controller.end_scene()
```

## Run with Human Input

To start the Unity application and enter your actions and parameters from the terminal, you can run the `mcs_run_in_human_input_mode` script that was installed in the package with the MCS Python Library (the `mcs_unity_build_file` is the executable):

```
mcs_run_in_human_input_mode <mcs_unity_build_file> <mcs_config_json_file>
```

Run options:
- `--debug`
- `--noise`
- `--no_depth_masks`
- `--no_object_masks`
- `--seed <python_random_seed>`

## Run with Scene Timer

To run the Unity application and measure your runtime speed, you can run the `mcs_run_scene_timer` script that was installed in the package with the MCS Python Library:

```
mcs_run_scene_timer <mcs_unity_build_file> <mcs_config_file_folder> <debug=False>
```

This will run all of the MCS scene configuration JSON files in the given folder, use the PASS action for 20 steps (or for a number of steps equal to the last_step of the config file's goal, if any) in each scene, and print out the total, average, minimum, and maximum run time for all the scenes and the steps.

## Documentation

[API.md](./API.md)

## Example Scene Configuration Files

[scenes/README.md](./scenes/README.md)

## Development README

[machine_common_sense/README.md](./machine_common_sense/README.md)

## Troubleshooting

[mcs-ta2@machinecommonsense.com](mailto:mcs-ta2@machinecommonsense.com)

