# Machine Common Sense Web Browser Demo

This MCS web app lets you run scenes in your web browser, using your keyboard to move around and perform actions like an AI would.

## Usage

TODO

## Development

### Install

First, "git clone" this repository. Then run the following commands from this folder to setup your python environment:

```
python3 -m venv --prompt webenabled venv
source venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

If you are a developer for this software, we recommend you install the machine_common_sense library in editable mode:

```
python -m pip install -e ../
```

### Scene Files

Put scene json files into scenes/.   The directory will be scanned and the list of 
scene files will appear on the web page 

### Run Web Server

First, run `cache_addressables` to cache all addressable assets and prevent possible timeout issues. You should do this each time you reboot your machine.

Then, run `python mcsweb.py` to start the flask server with host `0.0.0.0` (so the page will be accessable from any machine on the network) and port `8080`.

Alternatively, run `python mcsweb.py` to see all of the available options. The `--debug` flag is very helpful for development.

Then, on your machine, in your web browser, go to: `http://localhost:8080/mcs` (or, alternatively, `http://127.0.0.1:8080/mcs`).

If on another machine in the same network, then instead go to: `http://<machine.ip.address>:8080/mcs`

### Overview

1. Routing is done in `mcsweb`. Loading `localhost:8080/mcs` calls `show_mcs_page`. This uses `request.cookies` to identify new user sessions. A single `MCSInterface` is instantiated for each user session. The page is rendered using `templates/mcs_page.html`.
2. The `MCSInterface` class creates the `cmd_<time>/` and `output_<time>/` directories in `static/mcsinterface/` for the input and output data for the current user session. It starts a subprocess in a separate thread which runs `run_scene_with_dir.py`. It watches the `output_<time>/` directory for step output and images the subprocess saves in that directory, which are the images returned by action steps.
3. The `run_scene_with_dir` script creates the MCS Controller and starts a watchdog Observer to watch for changes to the `cmd_<time>/` directory. Whenever a new "command" text file is created or modified, it triggers the Observer, which reads the command (either a scene filename ending in ".json" or an MCS action like Pass or MoveAhead), gives it to the MCS Controller via either its `start_scene` or `step` function, and saves step output and the output image in the `output_<time>` directory.
4. When the user selects a scene in the UI, the `handle_scene_selection` function in `mcsweb` calls `load_scene` in `MCSInterface` which saves a "command" text file containing the scene filename.
5. When the user presses a key in the UI, the `handle_keypress` function in `mcsweb` calls `perform_action` in `MCSInterface` which saves a "command" text file containing the action string.

### Pyinstaller

Please note: Your python virtual environment must be installed in this folder (`venv/` is inside `webenabled/`) and activated.

#### Linux and Mac

##### Setup

```
pip install -U pyinstaller
```

##### Build

```
pyinstaller --add-data 'templates:templates' --add-data 'static:static' --add-data 'scenes:scenes' --console mcsweb.py --log-level=DEBUG &> pyinstaller.out
```

##### Run

```
./dist/mcsweb/mcsweb
```

##### Package

Unfortunately, you need to copy a bunch of files into the `dist/mcsweb/` folder before you begin packaging, in order for the application to run properly:

```
cp *.py dist/mcsweb/ ; cp config_level1.ini dist/mcsweb/ ; cp -r scenes/ dist/mcsweb/ ; cp -r static/ dist/mcsweb/ ; cp -r venv/ dist/mcsweb/
```

##### Cleanup

Do before you rebuild:

```
rm -rf build/ dist/
```

#### Windows

Same as the Linux/Mac instructions, except as noted below.

Build:

```
pyinstaller --add-data "templates;templates" --add-data "static;static" --add-data "scenes;scenes" --console mcsweb.py --log-level=DEBUG *>&1 | Tee-Object -Append -FilePath pyinstaller.out
```
