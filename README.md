[![PyPI version fury.io](https://badge.fury.io/py/machine-common-sense.svg)](https://pypi.python.org/pypi/machine-common-sense/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/machine-common-sense.svg)](https://pypi.python.org/pypi/machine-common-sense/)
[![Linux](https://svgshare.com/i/Zhy.svg)](https://svgshare.com/i/Zhy.svg)
[![macOS](https://svgshare.com/i/ZjP.svg)](https://svgshare.com/i/ZjP.svg)
[![Downloads](https://pepy.tech/badge/machine-common-sense)](https://pepy.tech/project/machine-common-sense)
[![Downloads](https://pepy.tech/badge/machine-common-sense/month)](https://pepy.tech/project/machine-common-sense)
[![PyPI license](https://img.shields.io/pypi/l/machine-common-sense.svg)](https://pypi.python.org/pypi/machine-common-sense/)

Master Unit Tests: [![Master](https://github.com/NextCenturyCorporation/MCS/actions/workflows/master-unit-tests.yaml/badge.svg)](https://github.com/NextCenturyCorporation/MCS/actions/workflows/master-unit-tests.yaml)

Development Unit Tests: [![Development](https://github.com/NextCenturyCorporation/MCS/actions/workflows/development-merge.yaml/badge.svg)](https://github.com/NextCenturyCorporation/MCS/actions/workflows/development-merge.yaml)

Publish Documentation: [![Publish Docs](https://github.com/NextCenturyCorporation/MCS/actions/workflows/docs-publish.yaml/badge.svg)](https://github.com/NextCenturyCorporation/MCS/actions/workflows/docs-publish.yaml)

Publish to PyPI: [![Publish PyPI](https://github.com/NextCenturyCorporation/MCS/actions/workflows/pypi-publish.yaml/badge.svg)](https://github.com/NextCenturyCorporation/MCS/actions/workflows/pypi-publish.yaml)

# MCS Python Package

Python interface for interacting with MCS AI2Thor environment and running scenes. The latest release of the MCS Python library is `0.5.6`. You can find the latest documentation [here](https://nextcenturycorporation.github.io/MCS).

- [Quickstart Installation](#quickstart-installation)
- [Usage](#usage)
- [Documentation](#documentation)
- [Other MCS GitHub Repositories](#other-mcs-github-repositories)
- [Troubleshooting/Email](#troubleshooting)
- [License](#apache-2-open-source-license)

## Quickstart Installation

### Virtual Environments

Python virtual environments are recommended when using the  Machine Common Sense package. All steps below presume the activation of the virtual environment. The developer can choose between traditional Python or Anaconda depending on need. These instructions work for Ubuntu Linux or MacOS. The MCS package has a minimum requirement of Python 3.7 regardless of Python distribution. As of 0.4.4, the MCS package will automatically download the Unity app release for that version. On the first run, the Unity app may take a while to start in order to download all the assets. 

#### Traditional Python Environment

```bash
$ python3.7 -m venv --prompt mcs venv
$ source venv/bin/activate
(venv) $ python -m pip install --upgrade pip setuptools wheel
```

#### Alternate Anaconda Environment

For developers using Anaconda Python distributions instead of traditional Python, create your project virtual environment from the base Anaconda environment.

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

With the activated Python virtual environment, install the MCS package from the git url.

```bash
(venv) $ python -m pip install machine-common-sense
```

### Sample MCS Config File

There may be additional settings you want to specify, which can be accomplished via the MCS configuration file. You can use the [sample_config.ini](./sample_config.ini) file to start. This file has the `metadata` level set to `oracle`, which ensures that the data for all objects in a scene is returned, as well as object masks. For the purposes of this guide, we will pass this along to the MCS controller via the `config_file_or_dict`, which is outlined in the `Usage` example below.

For more in-depth information on configuration files and more about the different properties within, see the documentation about the [MCS configuration file](https://nextcenturycorporation.github.io/MCS/install.html#mcs-configuration-file)

## Usage

Example usage of the MCS library:

```python
import machine_common_sense as mcs

# Unity app file will be downloaded automatically
controller = mcs.create_controller(config_file_or_dict='./some-path/sample_config.ini')

# Either load the scene data dict from an MCS scene config JSON file or create your own.
# We will give you the training scene config JSON files and the format to make your own.
scene_data = mcs.load_scene_json_file(scene_json_file_path)

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

## Documentation

- [Documentation Home](https://nextcenturycorporation.github.io/MCS)
- [Installation and Setup](https://nextcenturycorporation.github.io/MCS/install.html)
- [MCS Configuration File](https://nextcenturycorporation.github.io/MCS/install.html#mcs-configuration-file)
- [Example Usage](https://nextcenturycorporation.github.io/MCS/examples.html)
- [Python API](https://nextcenturycorporation.github.io/MCS/api.html)
- [Example Scene Configuration Files](https://nextcenturycorporation.github.io/MCS/scenes.html)
- [Scene Configuration JSON Schema](https://nextcenturycorporation.github.io/MCS/schema.html)
- [Developer Docs](https://nextcenturycorporation.github.io/MCS/dev.html)

## Other MCS GitHub Repositories

- [Unity code](https://github.com/NextCenturyCorporation/ai2thor)
- [Scene Generator](https://github.com/NextCenturyCorporation/mcs-scene-generator)
- [Data Ingest](https://github.com/NextCenturyCorporation/mcs-ingest)
- [Evaluation Dashboard (UI)](https://github.com/NextCenturyCorporation/mcs-ui)

## Troubleshooting

[mcs-ta2@machinecommonsense.com](mailto:mcs-ta2@machinecommonsense.com)

## Acknowledgements

This material is based upon work supported by the Defense Advanced Research Projects Agency (DARPA) and Naval Information Warfare Center, Pacific (NIWC Pacific) under Contract No. N6600119C4030. Any opinions, findings and conclusions or recommendations expressed in this material are those of the author(s) and do not necessarily reflect the views of the DARPA or NIWC Pacific.

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
