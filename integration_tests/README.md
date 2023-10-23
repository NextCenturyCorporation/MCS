# MCS Integration Tests

The goal of the integration tests is to:
- Verify specific sequences of actions entered via the MCS Python API return specific metadata outputs containing expected observation, navigation, and object interaction results within tightly-controlled scenes (the "Handmade" tests).
- Verify all objects that should be compiled into the given MCS Unity build actually exist in that build (the "Prefab" tests). Because the files for some objects (Unity Prefabs) are stored in a private repository and must be copied into the Resources folder before building, we want to verify that each object was correctly included.

## Run Handmade Tests

```
python run_handmade_tests.py
```

### Run Specific Unity Build

```
python run_handmade_tests.py --mcs_unity_build_file_path <mcs_unity_build_file_path>
```

### Run Specific Metadata Tier

```
python run_handmade_tests.py --mcs_unity_build_file_path <mcs_unity_build_file_path> --metadata <level1|level2|oracle>
```

### Run Specific Test Scene

```
python run_handmade_tests.py --mcs_unity_build_file_path <mcs_unity_build_file_path> --test 001
```

Replace `001` with any test scene.

## Run Prefab Tests

Note that this test requires an internet connection to run.

```
python run_prefab_tests.py
```

### Run on Development Branch

```
python run_prefab_tests.py --mcs_unity_version development
```

## Run the Autofixer

The autofixer will automatically fix any broken test cases and overwrite the test files. This is useful when you make a change to the simulation environment that you know will affect the specific numbers in the test cases. For example, if you were to change the performer agent's standing height, then the direction and distance numbers in the oracle output test cases will need to be adjusted accordingly.

Please make sure that you know what you're doing when you run the autofixer, so it doesn't "fix" a test case that's actually exposing a bug! You can also use the `--test` and `--metadata` arguments to run the autofixer on only specific test files. Remember to commit the modified files in the git repository.

```
python run_tests.py --mcs_unity_build_file_path <mcs_unity_build_file_path> --autofix
```

## Adding New Handmade Test Scenes

Create the following files (Replace `<X>` with your test name):

- `./data/<X>.scene.json`: An MCS scene configuration JSON file. Give it a useful `name` that describes the specific test case for future developers.
- `./data/<X>.actions.txt`: The list of specific actions to take in the scene, each action and its corresponding parameters on its own line, with the following format: `action<,parameter=value>\n`
- `./data/<X>.<level1|level2|oracle>.outputs.json`: Each file is a JSON list of expected step and object output metadata per action step, starting at step 0 (initialization), for runs with the file's corresponding metadata tier. Please do not skip any step. See the [Outputs File Schema](#Outputs-File-Schema) below for the available JSON test properties. One separate file per metadata tier, and each metadata tier should have its own corresponding file.
- (Optionally) `./data/<X>.<level1|level2|oracle>.config.ini`: MCS config files to use for running this specific scene at each metadata level, overriding the default config files in `integration_tests/`.

While adding a new test scene, you can run with the `--dev` flag to run the whole scene and print the errors at each action step (by default, a test will stop immediately if it finds an error).

### Outputs File Schema

#### Example

```json
[{
    "step_number": 0,
    "head_tilt": 0.0,
    "objects_count": 1,
    "position_x": 0.0,
    "position_y": 0.0,
    "position_z": 0.0,
    "return_status": "SUCCESSFUL",
    "rotation_y": 0.0,
    "structural_objects_count": 5,
    "objects": [{
        "id": "testObject",
        "held": true,
        "position_x": 0.0,
        "position_y": 0.0,
        "position_z": 1.0,
        "rotation_x": 0.0,
        "rotation_y": 0.0,
        "rotation_z": 1.0,
        "shape": "ball",
        "texture_color_list": ["blue"],
        "visible": true
    }]
}]
```

#### Notes

- Please have validation for each step.
- If you do not include checks for properties, it does not mean those properties are null, it just means you are not checking them in the particular test. This is also true for objects: if you put an empty array for `objects`, it does not mean there are no objects, it just means you are not checking any object properties (so use `objects_count: 0` instead).
- Any numerical property can be an array instead of a single number. The array must contain two numbers. The integration tests will use the numbers in the array as minimum and maximum values for validating the property at that step.
- All numerical properties will be rounded to the hundredths place.

#### Step Validation

- `action_list`: Expected action restrictions at this step, as an array of nested [action, parameters] array 
- `camera_height`: Expected camera height
- `haptic_feedback`: Expected haptick feedback
- `head_tilt`: Expected head tilt
- `holes`: Expected holes, as an array of nested [X, Z] arrays
- `lava`: Expected lava, as an array of nested [X, Z] arrays
- `objects`: Validation of specific objects; see [Object Validation](#Object-Validation) below. Note that each element in this array is required to have an `id` corresponding to the `id` of an object in the scene file.
- `objects_count`: Expected number of objects
- `physics_frames_per_second`: Expected physics frames per second
- `position_x`: Expected performer agent X position
- `position_y`: Expected performer agent Y position
- `position_z`: Expected performer agent Z position
- `return_status`: Expected action return status
- `resolved_object`: Expected resolved object
- `resolved_receptacle`: Expected resolved receptacle object
- `reward`: Expected reward
- `rotation_y`: Expected performer agent Y rotation
- `room_dimensions`: Expected room dimensions
- `step_number`: Expected step number
- `structural_objects`: Validation of specific structural objects; see [Object Validation](#Object-Validation) below. Note that each element in this array is required to have an `id` corresponding to the `id` of an object in the scene file.
- `structural_objects_count`: Expected number of structural objects
- `triggered_by_sequence_incorrect`: Expected "triggered_by_sequence_incorrect"

#### Object Validation

- `id` (Required): The "id" of the corresponding object in the scene file
- `associated_with_agent`: Whether this object starts held by a simulation-controlled agent
- `direction_x`: Expected X direction from the performer agent to this object
- `direction_y`: Expected Y direction from the performer agent to this object
- `direction_z`: Expected Z direction from the performer agent to this object
- `distance`: Expected distance between the performer agent and this object
- `held`: Whether this object is being held
- `is_open`: Whether this object is currently open
- `locked`: Whether this object is currently locked
- `mass`: Expected object mass
- `material_list`: Expected object salient material list
- `position_x`: Expected object X position
- `position_y`: Expected object Y position
- `position_z`: Expected object Z position
- `rotation_x`: Expected object X rotation
- `rotation_y`: Expected object Y rotation
- `rotation_z`: Expected object Z rotation
- `shape`: Expected object shape string (not to be confused with its "type" string)
- `simulation_agent_held_object`: Expected object this simulation-controlled agent starts holding
- `simulation_agent_is_holding_held_object`: Whether this simulation-controlled agent is still holding its object
- `state_list`: Expected object "states" at this step
- `texture_color_list`: Expected object texture colors
- `visible`: Whether this object is currently visible

Copyright 2023 CACI (formerly Next Century Corporation)
