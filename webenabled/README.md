# Running MCS on the web

## Install

First check out the project.  Then run the following commands to set up the environment.

```
python -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

## Scene Files

Put scene json files into scenes/.   The directory will be scanned and the list of 
scene files will appear on the web page 

## Run Web Server

For development, run flask directly, passing in command line options

```FLASK_APP=mcsweb FLASK_DEBUG=1 flask run --port=8080 --host=0.0.0.0```

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

