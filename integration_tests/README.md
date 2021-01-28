# MCS Integration Tests

The goal of the integration tests is to verify that specific sequences of actions entered via the MCS Python API lead to specific metadata outputs containing expected observation, navigation, and object interaction results.

## Run All Test Scenes

```
python run_tests.py <mucs_unity_build_file_path>
```

## Run Specific Metadata Tier

```
python run_tests.py <mucs_unity_build_file_path> --metadata <level1|level2|oracle>
```

## Run Specific Test Scene

```
python run_tests.py <mucs_unity_build_file_path> --test 001
```

Replace `001` with any test scene.

## Adding New Test Scenes

Create the following files (Replace `<X>` with your test name):

- `./data/<X>.scene.json`: MCS scene JSON file
- `./data/<X>.actions.txt`: List of actions to take in the scene, with the following format: `action<,parameter=value>\n`
- `./data/<X>.level1.outputs.json`, `./data/<X>.level2.outputs.json`, `./data/<X>.oracle.outputs.json`: JSON list of expected step and object output metadata per action step, starting at step 0 (initialization). Please do not skip any step. See the Python code for the available JSON test properties. One separate file per metadata tier.
