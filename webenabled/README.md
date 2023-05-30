# Running MCS on the web

## Install

First, "git clone" this repository. Then run the following commands from this folder to setup your python environment:

_(TODO: Remove the 4th line once 0.7.0 is released)_

```
python -m venv --prompt webenabled venv
source venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e ../
python -m pip install -r requirements.txt
```

If you are a developer for this software, we recommend you install the machine_common_sense library in editable mode:

```
python -m pip install -e ../
```

## Scene Files

Put scene json files into scenes/.   The directory will be scanned and the list of 
scene files will appear on the web page 

## Run Web Server

For development, run the server directly:

_(Note that we're calling `venv/bin/flask` to ensure it's the correct version of flask, which is especially important on Mac)_

```FLASK_APP=mcsweb FLASK_DEBUG=1 venv/bin/flask run --port=8080 --host=0.0.0.0```

Where:
- FLASK_APP is the name of the python file to run.
- FLASK_DEBUG=1 means that flask will auto-reload files when they change on disk
- port 8080 makes the port flask runs on be 8080, rather than default of 5000
- host=0.0.0.0 means that the page will be accessible from any machine, defaults to localhost

For production, use a WSGI server (not sure what to put here....)

## Use 

On same or other machine, go to:

```
http://<machine.ip.address>:8080/mcs
```

## Overview

1. Routing is done in `mcsweb`. Loading `localhost:8080/mcs` calls `show_mcs_page`. This uses `request.cookies` to identify new user sessions. A single `MCSInterface` is instantiated for each user session. The page is rendered using `templates/mcs_page.html`.
2. The `MCSInterface` class creates the `cmd_<time>/` and `img_<time>/` directories in `static/mcsinterface/` for the input and output data for the current user session. It starts a subprocess in a separate thread which runs `run_scene_with_dir.py`. It watches the `img_<time>/` directory for images the subprocess saves in that directory, which are the images returned by action steps.
3. The `run_scene_with_dir` script creates the MCS Controller and starts a watchdog Observer to watch for changes to the `cmd_<time>/` directory. Whenever a new "command" text file is created or modified, it triggers the Observer, which reads the command (either a scene filename ending in ".json" or an MCS action like Pass or MoveAhead), gives it to the MCS Controller via either its `start_scene` or `step` function, and saves the output image in the `img_<time>` directory.
4. When the user selects a scene in the UI, the `handle_scene_selection` function in `mcsweb` calls `load_scene` in `MCSInterface` which saves a "command" text file containing the scene filename.
5. When the user presses a key in the UI, the `handle_keypress` function in `mcsweb` calls `perform_action` in `MCSInterface` which saves a "command" text file containing the action string.
