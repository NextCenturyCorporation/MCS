
Installation and Setup
=======================

.. _Download and unzip the Mac ZIP: https://github.com/NextCenturyCorporation/MCS/releases/download/0.4.3/MCS-AI2-THOR-Unity-App-v0.4.3-mac.zip
.. _Download and unzip the Linux ZIP: https://github.com/NextCenturyCorporation/MCS/releases/download/0.4.3/MCS-AI2-THOR-Unity-App-v0.4.3-linux.zip

Virtual Environments
------------------------

Python virtual environments are recommended when using the MCS package. All steps below presume the activation of the virtual environment. The developer can choose between traditional Python or Anaconda depending on need. These instructions are for Ubuntu Linux or MacOS. The Machine Common Sense package has a minimum requirement of Python 3.6 regardless of Python distribution.

Traditional Python Environment
*******************************

.. code-block:: console

    $ python3.6 -m venv venv
    $ source venv/bin/activate
    (venv) $ python -m pip install --upgrade pip setuptools wheel


Alternate Anaconda Environment
*******************************

For developers using Anaconda Python distributions instead of traditional Python, create your project virtual environment from the base Anaconda environment.

.. code-block:: console

    (base) $ conda create -n myenv python=3.8
    (base) $ conda env list
    # conda environments:
    #
    base                  *  /home/user/anaconda3
    myenv                    /home/user/anaconda3/envs/myenv
    (base) $ conda activate myenv
    (myenv) $


Install MCS
-----------

With the activated Python virtual environment, install the MCS package:

.. code-block:: console

    (venv) $ python -m pip install machine-common-sense

For older versions prior to 0.4.3, you will need to use the git URL with the appropriate version number:

.. code-block:: console

    (venv) $ python -m pip install git+https://github.com/NextCenturyCorporation/MCS@0.4.2#egg=machine_common_sense


Download Unity Release
----------------------

Our Unity App is built for Linux or Mac. There is no Windows support currently.

As of release 0.4.4, the latest Unity version will be downloaded for you automatically by the MCS package. We have also switched to using addressables for our Unity release, which increases the initial startup time for Unity application on the first run. If this all sounds fine, feel free to skip this section, but if you'd like to know more about addressables or are using a release prior to 0.4.4, please follow the instructions below:

The links below are referencing version |version|. For our previous releases, please see `this page <https://github.com/NextCenturyCorporation/MCS/releases>`_.


Linux Version:
**************

1. `Download and unzip the Linux ZIP`_ *Note that for versions prior to 0.4.3, the Unity Linux build and the data directory are in two separate zips.*

2. Ensure that the Unity App, the Data Directory TAR, and the UnityPlayer.so file are all in the same directory.

3. Untar the Data Directory:

.. parsed-literal::

    tar -xzvf MCS-AI2-THOR-Unity-App-v\ |version|\ _Data.tar.gz


4. Mark the Unity App as executable:

.. parsed-literal::

    chmod a+x MCS-AI2-THOR-Unity-App-v\ |version|\ .x86_64


Mac Version:
************

`Download and unzip the Mac ZIP`_


Addressables
************

As of 0.4.4, we are using addressable assets that are stored remotely on AWS, greatly decreasing the size of our Unity releases. This also means that there is a bit of a trade off on first-time start up when you download a new release, since the resources will have to be downloaded. If you would like to avoid this load time on initial start up (which could result in a timeout), you can download the latest release using the links above, and then run the `cache-addressables.py <https://github.com/NextCenturyCorporation/MCS/blob/master/scripts/cache_addressables.py>`_ script:

.. code-block:: console

    python ./scripts/cache_addressables.py ~/path/to/unity/app


Pass Unity App Location to MCS
*******************************
After downloading the Unity app, you will need to reference the path using the `unity_app_file_path` property when using the MCS package (outlined on the :doc:`Examples <examples>` page). While the path to the Unity app on Linux is pretty straightforward, the path for the Mac version executable is actually within the Contents/ directory level of your download:

.. parsed-literal::

    ./MCS-AI2-THOR-Unity-App-v\ |version|\.app/Contents/MacOS/MCS-AI2-THOR 


MCS Configuration File
----------------------

To use an MCS configuration file, you can either pass in a file path via the `config_file_path` property in the create_controller() method, or set the `MCS_CONFIG_FILE_PATH` environment variable to the path of your MCS configuration file (note that the configuration must be an INI file -- see `sample_config.ini <https://github.com/NextCenturyCorporation/MCS/blob/master/sample_config.ini>`_ for an example).

Config File Properties
**********************

history_enabled
^^^^^^^^^^^^^^^

(boolean, optional)

Whether to save the scene history output data in your local directory. Default: True

metadata
^^^^^^^^

(string, optional)

The `metadata` property describes what metadata will be returned by the MCS Python library. The `metadata` property is available so that users can run baseline or ablation studies during training. It can be set to one of the following strings:

- `oracle`: Returns the metadata for all the objects in the scene, including visible, held, and hidden objects. Object masks will have consistent colors throughout all steps for a scene.
- `level2`: Only returns the images (with depth maps AND object masks), camera info, and properties corresponding to the player themself (like head tilt or pose). No information about specific objects will be included. Note that here, object masks will have randomized colors per step.
- `level1`: Only returns the images (with depth maps but NOT object masks), camera info, and properties corresponding to the player themself (like head tilt or pose). No information about specific objects will be included.
- `none`: Only returns the images (but no depth maps or object masks), camera info, and properties corresponding to the player themself (like head tilt or pose). No information about specific objects will be included.

If no metadata level is set:
- `default`: Fallback if no metadata level is specified. Only meant for use during development (evaluations will never be run this way). Includes metadata for visible and held objects in the scene, as well as camera info and properties corresponding to the player. Does not include depth maps or object masks.

noise_enabled
^^^^^^^^^^^^^^^

(boolean, optional)

Whether to add random noise to the numerical amounts in movement and object interaction action parameters. Will default to `False`.

save_debug_images
^^^^^^^^^^^^^^^^^

(boolean, optional)

Save RGB frames, depth masks, and object instance segmentation masks (if returned in the output by the chosen metadata tier) to image files on each step. Default: False

save_debug_json
^^^^^^^^^^^^^^^

(boolean, optional)

Save AI2-THOR/Unity input, AI2-THOR/Unity output, and MCS StepMetadata output to JSON file on each step. Default: False

seed
^^^^

(int, optional)

A seed for the Python random number generator (defaults to None).

size
^^^^

(int, optional)

Desired screen width. If value given, it must be more than `450`. If none given, screen width will default to `600`.

video_enabled
^^^^^^^^^^^^^

(boolean, optional)

Create and save videos of the RGB frames, depth masks, object instance segmentation masks (if returned in the output by the chosen metadata tier), 2D top-down scene views, and the heatmap images given to us in `make_step_prediction` by the AI performer. Default: False

Example Using the Config File to Generate Scene Graphs or Maps
**************************************************************

1. Reference or copy the `sample_config.ini <https://github.com/NextCenturyCorporation/MCS/blob/master/sample_config.ini>`_ or save your .ini MCS configuration file with:

.. code-block:: console

    [MCS]
    metadata: oracle

2. Create a simple Python script to loop over one or more JSON scene configuration files, load each scene in the MCS controller, and save the output data in your own scene graph or scene map format.

.. code-block:: python

    import os
    import machine_common_sense as mcs

    os.environ['MCS_CONFIG_FILE_PATH'] = # Path to your MCS configuration file

    scene_files = # List of scene configuration file paths

    controller = mcs.create_controller()

    for scene_file in scene_files:
        scene_data, status = mcs.load_scene_json_file(scene_file)

        if status is not None:
            print(status)
        else:
            output = controller.start_scene(scene_data)
            # Use the output to save your scene graph or map

