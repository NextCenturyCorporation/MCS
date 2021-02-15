# MCS Integration Tests

The goal of the integration tests is to:
- Verify specific sequences of actions entered via the MCS Python API return specific metadata outputs containing expected observation, navigation, and object interaction results within tightly-controlled scenes (the "Handmade" tests).
- Verify all objects that should be compiled into the given MCS Unity build actually exist in that build (the "Prefab" tests). Because the files for some objects (Unity Prefabs) are stored in a private repository and must be copied into the Resources folder before building, we want to verify that each object was correctly included.

## Run Handmade Tests

```
python run_handmade_tests.py <mcs_unity_build_file_path>
```

### Run Specific Metadata Tier

```
python run_handmade_tests.py <mcs_unity_build_file_path> --metadata <level1|level2|oracle>
```

### Run Specific Test Scene

```
python run_handmade_tests.py <mcs_unity_build_file_path> --test 001
```

Replace `001` with any test scene.

## Run Prefab Tests

TODO MCS-432

## Run All Tests

```
python run_tests.py <mcs_unity_build_file_path>
```

## Adding New Handmade Test Scenes

Create the following files (Replace `<X>` with your test name):

- `./data/<X>.scene.json`: An MCS scene configuration JSON file. Give it a useful `name` that describes the specific test case for future developers.
- `./data/<X>.actions.txt`: The list of specific actions to take in the scene, each action and its corresponding parameters on its own line, with the following format: `action<,parameter=value>\n`
- `./data/<X>.<level1|level2|oracle>.outputs.json`: Each file is a JSON list of expected step and object output metadata per action step, starting at step 0 (initialization), for runs with the file's corresponding metadata tier. Please do not skip any step. See the Python code for the available JSON test properties. One separate file per metadata tier, and each metadata tier should have its own corresponding file.

While adding a new test scene, you can run with the `--dev` flag to run the whole scene and print the errors at each action step (by default, a test will stop immediately if it finds an error).

### Future Handmade Test Scene Ideas

- Ramp movement (MCS-472)
- PickupObject on a container with an object positioned inside of it (MCS-473)
- Circumnavigating objects (MCS-541)
- Self teleportation (MCS-540)
- PullObject, various mass and force (when needed by an evaluation task)
- PushObject, various mass and force (when needed by an evaluation task)
- ThrowObject, various mass and force (when needed by an evaluation task)
- Change pose between Stand, Crawl, and LieDown (when needed by an evaluation task)
- Crawl under a table that is too short to be walked under (when needed by an evaluation task)
- PickupObject on a "pickupable" object that is too large or heavy (when needed by an evaluation task)
