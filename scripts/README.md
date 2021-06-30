# Developer Scripts

## Run Scripts

The following Python scripts use subclasses of RunnerScript from [`runner_script.py`](./runner_script.py) to run one or more MCS scenes sequentially. Use `--help` on any script to see a full list of command line options.

### Single File

Runs a single given scene file.

- [`run_action_file.py`](./run_action_file.py`) Runs a scene using a given action file, which is a text file containing one or more lines, each line with an MCS action and parameters (like `Pass` or `PickupObject,objectId=ball`).
- [`run_just_pass.py`](./run_just_pass.py) Just uses the Pass action until the scene's last step. Useful for passive scenes that only require passing.
- [`run_just_rotate.py`](./run_just_rotate.py) Just uses a Rotate action 36 times to spin around in a circle. Useful for interactive scenes.
- [`run_last_action.py`](./run_last_action.py) Runs the last action (element) from the scene's action list (array) that's returned on each step. Useful for passive scenes that require specific actions run on specific steps (like passive agent scenes that require EndHabituation actions on some steps).

Example:

```
python run_just_pass.py --mcs_unity_build_file <path_to_unity_build> <path_to_json_scene>
```

### Multiple File

Runs all of the `_debug.json` files found using a given file prefix. For example, if the given file prefix is `./folder/file_`, and `folder/` contains `file_1.json`, `file_1_debug.json`, `file_2.json`, and `file_2_debug.json`, then the script will run `file_1_debug.json` and `file_2_debug.json`.

- [`run_interactive_scenes.py`](./run_interactive_scenes.py) Just uses a Rotate action 36 times to spin around in a circle for each given scene.
- [`run_passive_scenes.py`](./run_passive_scenes.py) Runs the last action (element) from the scene's action list (array) that's returned on each step.
- [`run_reorientation_scenes.py`](./run_reorientation_scenes.py) Runs specific actions for reorientation scenes.

Example:

```
python run_passive_scenes.py --mcs_unity_build_file <path_to_unity_build> <prefix_to_json_scene>
```

#### Generating Example Hypercube Videos

Use the following command line options:

- `--debug` Saves output images of each action/frame/step to file.
- `--save-videos` Creates a video from all the output images after running each scene.
- `--rename <prefix>` Renames the output files to use the given file prefix.

Example:

```
python run_passive_scenes.py --mcs_unity_build_file <path_to_unity_build> <prefix_to_json_scene> --debug --save-videos --rename EX_1
```

