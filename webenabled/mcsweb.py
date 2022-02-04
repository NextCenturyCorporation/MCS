from flask import Flask, render_template, request, session
from flask import jsonify
# See: https://www.geeksforgeeks.org/how-to-use-flask-session-in-python-flask/
from flask_session import Session

from mcs_interface import MCSInterface

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

    # app.logger.warning(f'values in request: {key}')
    return data


@app.before_first_request
def before_first():
    # Because we are using filesystem session, it keeps track of
    # sessions between start ups.  So clear it out when we start.
    for key in list(session.keys()):
        print(f"Have session key: {key}")
    session.clear()


@app.route('/mcs')
def show_mcs_page():
    # is this a new session?   If so start up
    if not session.get("mcs_interface"):
        mcs_interface = MCSInterface()
        mcs_interface.start_mcs()
        session["mcs_interface"] = mcs_interface
    mcs_interface = session.get("mcs_interface")
    img = mcs_interface.get_latest_image()
    scene_list = mcs_interface.get_scene_list()

    # app.logger.warning(f'sending pic {rand_pic}')
    return render_template('mcs_page.html', unityimg=img, scene_list=scene_list)


@app.route("/keypress", methods=["POST"])
def handle_keypress():
    key = clean_request(request)
    mcs_interface = session.get("mcs_interface")
    img_name = mcs_interface.perform_action(key)
    resp = jsonify(img_name)
    return resp


@app.route("/scene_selection", methods=["POST"])
def handle_scene_selection():
    # Get the passed key, cleaning it up first
    scene_filename = clean_request(request)
    app.logger.warning(f'opening scene {scene_filename}')
    mcs_interface = session.get("mcs_interface")
    img_name = mcs_interface.load_scene("scenes/" + scene_filename)
    resp = jsonify(img_name)
    return resp
