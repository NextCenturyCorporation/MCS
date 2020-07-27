# MCS Sphinx Documentation

- Good Tutorial for Sphinx Clarity: https://medium.com/@richdayandnight/a-simple-tutorial-on-how-to-document-your-python-project-using-sphinx-and-rinohtype-177c22a15b5b
- Markdown Builder: https://pypi.org/project/sphinx-markdown-builder/

- Sphinx: https://www.sphinx-doc.org/en/master/
- Sphinx's own Tutorial: https://www.sphinx-doc.org/en/master/usage/quickstart.html


## Setup
1. Cd to `python_api` to make a virtual enviornment inside the folder: `virtualenv -p python3 <name of virtualenv>` 

2. Switch to the virtual enviornment: `source <name of virtualenv>/bin/activate`

3. pip install the requirements.txt

4. pip3 install sphinx-markdown-builder

5. mkdir docs --- cd docs

6. sphinx-quickstart

7. within docs open folder `source`. Copy paste this to the conf.py:

# -*- coding: utf-8 -*-
#
import os
import sys
sys.path.insert(0, os.path.abspath('../../'))

# -*- coding: utf-8 -*-
#
import os
import sys
sys.path.insert(0, os.path.abspath('../../'))

# -- Project information -----------------------------------------------------

project = 'Machine Common Sense'
copyright = '2020, DARPA'
author = 'DARPA'

# The short X.Y version
version = ''
# The full version, including alpha/beta/rc tags
release = ''


# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.todo',
    'sphinx.ext.githubpages',
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.ifconfig',
    'sphinx.ext.viewcode',
    'recommonmark'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = {
    '.rst': 'restructuredtext',
    '.txt': 'markdown',
    '.md': 'markdown',
}

# The master toctree document.
master_doc = 'index'

language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path .
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

html_static_path = ['_static']

# html_sidebars = {}
html_theme = 'classic'

-------------------------------------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------------------------------------------------
8. copy paste this into index.rst:

.. MCS documentation master file, created by
   sphinx-quickstart
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


MCS Documentation
===================
**************************
.. toctree::
   :maxdepth: 2


_init_
=====================
.. automodule:: machine_common_sense.__init__
   :members:

mcs
=================
.. automodule:: machine_common_sense.mcs
   :members:

mcs_action
===================
.. automodule:: machine_common_sense.mcs_action
   :members:

mcs_action_api_desc
=====================
.. automodule:: machine_common_sense.mcs_action_api_desc
   :members:

mcs_action_keys
=====================
.. automodule:: machine_common_sense.mcs_action_keys
   :members:

mcs_controller
=================
.. automodule:: machine_common_sense.mcs_controller
   :members:

mcs_controller_ai2thor
=======================
.. automodule:: machine_common_sense.mcs_controller_ai2thor
   :members:

mcs_goal
===================
.. automodule:: machine_common_sense.mcs_goal
   :members:

mcs_goal_category
=====================
.. automodule:: machine_common_sense.mcs_goal_category
   :members:

mcs_material
=================
.. automodule:: machine_common_sense.mcs_material
   :members:

mcs_object
===================
.. automodule:: machine_common_sense.mcs_object
   :members:

mcs_pose
===================
.. automodule:: machine_common_sense.mcs_pose
   :members:

mcs_return_status
=====================
.. automodule:: machine_common_sense.mcs_return_status
   :members:

mcs_reward
=================
.. automodule:: machine_common_sense.mcs_reward
   :members:

mcs_scene_history
===================
.. automodule:: machine_common_sense.mcs_scene_history
   :members:

mcs_step_output
===================
.. automodule:: machine_common_sense.mcs_step_output
   :members:

mcs_util
===================
.. automodule:: machine_common_sense.mcs_util
   :members:

run_mcs_environment
=====================
.. automodule:: machine_common_sense.run_mcs_environment
   :members:

run_mcs_eval_samples
=====================
.. automodule:: machine_common_sense.run_mcs_eval_samples
   :members:

run_mcs_human_input
=====================
.. automodule:: machine_common_sense.run_mcs_human_input
   :members:

run_mcs_intphys_samples
========================
.. automodule:: machine_common_sense.run_mcs_intphys_samples
   :members:

run_mcs_just_pass
===================
.. automodule:: machine_common_sense.run_mcs_just_pass
   :members:

run_mcs_just_rotate
====================
.. automodule:: machine_common_sense.run_mcs_just_rotate
   :members:

run_mcs_last_action
====================
.. automodule:: machine_common_sense.run_mcs_last_action
   :members:

run_mcs_scene_timer
====================
.. automodule:: machine_common_sense.run_mcs_scene_timer
   :members:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


-------------------------------------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------------------------------------


8. In docs run: `make html` or....

9. In docs run: `make markdown`

10. There are usually errors, if you cannot build you are missing exstentions. Copy paste the error and google it. Do what the internet says.

11. Navigate to build folder in docs. There is a markdown folder. Open the .md ........or............

12. Navigate to build folder in docs. There is an html folder which has `index`. Open that for html

