# MCS Python Library: Usage README

## Download

### Python Library

```
pip install git+https://github.com/NextCenturyCorporation/MCS@latest
```

### Unity Application

TODO

## Import

Code Example:

```python
from machine_common_sense import MCS

# Either load the config data dict from an MCS config JSON file or create your own.
# We will give you the training config JSON files and the format to make your own.
config_data = MCS.load_config_json_file(config_json_file_path)

# We will give you the Unity app file.
controller = MCS.create_controller(unity_app_file_path)

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

## Run with Human Input

To start the Unity application and enter your actions and parameters from the terminal, you can run the `mcs_run_in_human_input_mode` script that was installed in the package with the MCS Python Library:

```
mcs_run_in_human_input_mode <mcs_unity_build_file> <mcs_config_json_file>
```

## Documentation

[API.md](./API.md)

## Example Scene Configuration Files

[scenes/README.md](./scenes/README.md)

## Development README

[machine_common_sense/README.md](./machine_common_sense/README.md)

