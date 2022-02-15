from logging.config import dictConfig

from flask import Flask, session, jsonify, request, render_template
# See: https://www.geeksforgeeks.org/how-to-use-flask-session-in-python-flask/
from flask_session import Session

# Configure logging _before_ creating the app oject
# https://flask.palletsprojects.com/en/2.0.x/logging/
from mcs_interface import MCSInterface

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


def clean_request(response):
    """When we get a response from the client, it is mess
    and wrapped in weird ways.  Clean it up."""

    # Request data comes as binary, convert to text
    data = request.data.decode("utf-8")

    # Request data has quotes around it, remove them.
    if data[0] == '"' and data[len(data) - 1] == '"':
        data = data[1:len(data) - 1]

    # app.app.logger.warning(f'values in request: {key}')
    return data


@app.before_first_request
def before_first():
    # Because we are using filesystem session, it keeps track of
    # sessions between start ups.  So clear it out when we start.
    app.logger.warn("Got to here!!!!!!!")
    for key in list(session.keys()):
        app.logger.info(f"Have session key: {key}")
        session.pop(key)
    session.clear()


@app.route('/mcs')
def show_mcs_page():
    # is this a new session?   If so start up
    if not session.get("mcs_interface"):
        app.logger.info("Creating new session")
        mcs_interface = MCSInterface()
        mcs_interface.start_mcs()
        session["mcs_interface"] = mcs_interface
    mcs_interface = session.get("mcs_interface")
    if mcs_interface is None:
        app.logger.warn("Unable to load mcs_interface")
        return
    app.logger.info("Reading in session")
    img = mcs_interface.get_latest_image()
    scene_list = mcs_interface.get_scene_list()

    return render_template('mcs_page.html', unityimg=img, scene_list=scene_list)


@app.route("/keypress", methods=["POST"])
def handle_keypress():
    key = clean_request(request)
    mcs_interface = session.get("mcs_interface")
    if mcs_interface is None:
        app.logger.warn("Unable to load mcs_interface")
        return
    img_name = mcs_interface.perform_action(key)
    resp = jsonify(img_name)
    return resp


@app.route("/scene_selection", methods=["POST"])
def handle_scene_selection():
    # Get the passed key, cleaning it up first
    scene_filename = clean_request(request)
    app.logger.warning(f'opening scene {scene_filename}')
    mcs_interface = session.get("mcs_interface")
    img_name, action_list = mcs_interface.load_scene("scenes/" + scene_filename)
    resp = jsonify(action_list=action_list)

    # TODO:  Figure out how to send multiple values.
    # resp = jsonify(img_name=img_name, action_list=action_list)
    return resp
