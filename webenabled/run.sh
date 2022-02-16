#!/bin/bash

source ./venv/bin/activate

export FLASK_ENV=development
export FLASK_APP=mcsweb

# Set the debug level (0=off, 1=on)
export FLASK_DEBUG=0
# export FLASK_DEBUG=1

flask run --port=8080 --host=0.0.0.0 2>&1
