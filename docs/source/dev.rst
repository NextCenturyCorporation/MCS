Package Developer Notes
=======================

Package Installation
--------------------

Create a Virtual Environment
****************************

.. code-block:: console

    $ python3.7 -m venv --prompt mcs venv
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

Testing TopDown Plots
---------------------

The plotter module has a main which is only executed when the plotter module is run directly vs imported. The developer can provide a scene file as a positional argument and the plotter's main will run with video_enabled for 1 step. This will create a visual, depth and topdown video in a scene folder for quick review.

.. code-block:: bash

    (venv) $ python plotter.py playroom.json


More Config Options
---------------------------

Outlined here is a list of config file options that can be used **in addition** to the ones listed under the :ref:`MCS Config File` section.

To use a specific configuration, you can either pass in a file path or dictionary of values via the `config_file_or_dict` in the create_controller() method, or set the `MCS_CONFIG_FILE_PATH` environment variable to the path of your MCS configuration file (note that the configuration must be an INI file -- see `sample_config.ini <https://github.com/NextCenturyCorporation/MCS/blob/master/sample_config.ini>`_ for an example).

The `MCS_CONFIG_FILE_PATH` environment variable is meant for use by the TA2 team during evaluation.

Developer Config File Properties
********************************

evaluation_name
^^^^^^^^^^^^^^^

(string)

Identifier to add to scene history and video files (default: '').

team
^^^^

(string)

Team name identifier to prefix to scene history and video files (default: '').


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

Please see the following `Confluence page <https://nextcentury.atlassian.net/wiki/spaces/MCS/pages/1442742340/MCS+Release+Procedures>`_

