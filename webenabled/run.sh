#!/bin/bash

source ./venv/bin/activate

export FLASK_ENV=development
export FLASK_APP=mcsweb
export FLASK_DEBUG=1
flask run --port=8080 --host=0.0.0.0 2>&1
