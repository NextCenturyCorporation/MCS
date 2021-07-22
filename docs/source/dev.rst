Package Developer Notes
=======================

Package Installation
--------------------

Create a Virtual Environment
****************************

.. code-block:: console

    $ python3.6 -m venv --prompt mcs venv
    $ source venv/bin/activate
    (mcs) $ python -m pip install --upgrade pip setuptools wheel


Install the MCS Package and dependencies
****************************************

Install the packages included in the requirements file so that linting and documentation work. The requirements.txt file includes developer and package dependencies.

.. code-block:: console

    (mcs) $ python -m pip install -r requirements.txt

From the MCS root folder, install the package in your virtual environment in editable mode (-e) so that local changes will automatically reflect in the virtual environment.

.. code-block:: console

    (mcs) $ python -m pip install -e .

Run pre-commit
**************

Run pre-commit install to set up the git hooks for linting and auto-documentation.

.. code-block:: console

    (mcs) $ pre-commit install


Linting
-------

We are currently using `flake8 <https://flake8.pycqa.org/en/latest/>`_ and `autopep8 <https://pypi.org/project/autopep8/>`_ for linting and formatting our Python code. This is enforced within the python_api and scene_generator projects. Both are `PEP 8 <https://www.python.org/dev/peps/pep-0008/>`_ compliant (besides some inline exceptions), although we are ignoring the following rules:
- **E402**: Module level import not at top of file
- **W504**: Line break occurred after a binary operator

A full list of error codes and warnings enforced can be found `here <https://flake8.pycqa.org/en/latest/user/error-codes.html>`_

Both have settings so that they should run on save within Visual Studio Code `settings.json <https://github.com/NextCenturyCorporation/MCS/blob/master/.vscode/settings.json>`_ as well as on commit after running `pre-commit install` (see `.pre-commit-config.yaml <https://github.com/NextCenturyCorporation/MCS/blob/master/.pre-commit-config.yaml>`_ and `.flake8 <https://github.com/NextCenturyCorporation/MCS/blob/master/.flake8>`_), but can also be run on the command line:


.. code-block:: console

    (mcs) $ flake8

and

.. code-block:: console

    (mcs) $ autopep8 --in-place --aggressive --recursive <directory>

or

.. code-block: console

    (mcs) $ autopep8 --in-place --aggressive <file>


Testing
-------

See our `tests README <https://github.com/NextCenturyCorporation/MCS/blob/master/tests/README.md>`_

Sphinx Documentation
--------------------

- Good Sphinx Tutorial: https://medium.com/@richdayandnight/a-simple-tutorial-on-how-to-document-your-python-project-using-sphinx-and-rinohtype-177c22a15b5b
- Markdown Builder: https://pypi.org/project/sphinx-markdown-builder/
- Sphinx: https://www.sphinx-doc.org/en/master/
- Sphinx's own Tutorial: https://www.sphinx-doc.org/en/master/usage/quickstart.html

Python Style Guide
------------------

See https://numpydoc.readthedocs.io/en/latest/format.html

Running
-------

We have made multiple run scripts:

To run a script (like `run_human_input.py`) from the terminal with visual output:

.. code-block:: console

    (mcs) $ run_in_human_input_mode <mcs_unity_build_file> <mcs_config_json_file>


To run it headlessly, first install xvfb (on Ubuntu, run `sudo apt-get install xvfb`), then:

.. code-block:: console

    (mcs) $ xvfb-run --auto-servernum --server-args='-screen 0 640x480x24' python3 run_human_input.py <mcs_unity_build_file> <mcs_config_json_file>

Each run will generate a subdirectory (named based on your config file) containing the output image files from each step.

Making GIFs
-----------

First, install ffmpeg. Then (change the frame rate with the `-r` option):

.. code-block:: bash

    $ ffmpeg -r 3 -i frame_image_%d.png output.gif

Logging
-------

MCS uses the python logging package with some defaults.  Logging should be initialized via the mcs.init_logging() method if logging is desired.  the mcs.init_logging function have two parameters, log_config, and log_config_file.  The first is a dictionary and the second is a path to a file.  Both of these should contain a dictionary that contains the logging configuration of python logging. (https://docs.python.org/3/library/logging.config.html#logging-config-dictschema)  The log_config_file, if it exists, will always override the dictionary and defaults to log.config.user.py in the current working directory.  In most cases, one of the examples below should be used. 

Common examples of logging initialization:

.. code-block:: python

    # Below initializes default which logs to console
    mcs.init_logging()

    # Below initializes development default with file logging as well as console logging
    mcs.init_logging(LoggingConfig.get_dev_logging_config())

    #Below initializes error only console logging
    mcs.init_logging(LoggingConfig.get_errors_only_console_config())
    
Full List of Config Options
---------------------------

Outlined here is a comprehensive list of config file options that can be used.

To use an MCS configuration file, you can either pass in a file path via the `config_file_path` property in the create_controller() method, or set the `MCS_CONFIG_FILE_PATH` environment variable to the path of your MCS configuration file (note that the configuration must be an INI file -- see `sample_config.ini <https://github.com/NextCenturyCorporation/MCS/blob/master/sample_config.ini>`_ for an example).

Config File Properties
**********************

history_enabled
^^^^^^^^^^^^^^^

(boolean, optional)

Whether to save the scene history output data in your local directory. Default: True

metadata
^^^^^^^^

(string)

The `metadata` property describes what metadata will be returned by the MCS Python library. This can also be specified via the `MCS_METADATA_LEVEL` environment variable. It can be set to one of the following strings:

- `oracle`: Returns the metadata for all the objects in the scene, including visible, held, and hidden objects. Object masks will have consistent colors throughout all steps for a scene.
- `level2`: Only returns the images (with depth masks AND object masks), camera info, and properties corresponding to the player themself (like head tilt or pose). No information about specific objects will be included. Note that here, object masks will have randomized colors per step.
- `level1`: Only returns the images (with depth masks but NOT object masks), camera info, and properties corresponding to the player themself (like head tilt or pose). No information about specific objects will be included.
- `none`: Only returns the images (but not the masks), camera info, and properties corresponding to the player themself (like head tilt or pose). No information about specific objects will be included.

If no metadata level is set:
- `default`: Fallback if no metadata level is specified. Only meant for use during development (evaluations will never be run this way). Includes metadata for visible and held objects in the scene, as well as camera info and properties corresponding to the player. Does not include depth maps or object masks.

noise_enabled
^^^^^^^^^^^^^

(boolean)

Whether to add random noise to the numerical amounts in movement and object interaction action parameters. Will default to `False`.

seed
^^^^

(int)

A seed for the Python random number generator (defaults to None).

size
^^^^

(int)

Desired screen width. If value given, it must be more than `450`. If none given, screen width will default to `600`.


Handling Pull Requests From Contributors
----------------------------------------

Checkout the pull request from github

.. code-block:: bash

    $ git fetch origin +refs/pull/<pull#>/merge


If there are any package dependency changes, create a new virtual environment using the initialization steps above. Even if there aren't, it would be a good to start with a fresh environment anyway.

Run the unit tests locally

.. code-block:: console

    (mcs) $ python -m unittest


If the unit tests pass, then ensure the new code is solves the issue in the PR and follows our coding conventions. 

Be sure that PEP-8 formatting is correct or is easily fixable.

.. code-block:: console

    (mcs) $ flake8

After iterating with the contributor, if you feel the PR is reasonably close, feel free to approve the PR, merge, and fix any lingering issues.

Releases
--------

Update the version number in the following files:

- `CPU_Container.dockerfile <https://github.com/NextCenturyCorporation/MCS/blob/master/CPU_Container.dockerfile>`_
- `Dockerfile <https://github.com/NextCenturyCorporation/MCS/blob/master/Dockerfile>`_
- `README.md <https://github.com/NextCenturyCorporation/MCS/blob/master/README.md>`_
- `requirements.txt <https://github.com/NextCenturyCorporation/MCS/blob/master/requirements.txt>`_
- `setup.py <https://github.com/NextCenturyCorporation/MCS/blob/master/setup.py>`_
- `machine_common_sense/_version.py <https://github.com/NextCenturyCorporation/MCS/blob/master/machine_common_sense/_version.py>`_
