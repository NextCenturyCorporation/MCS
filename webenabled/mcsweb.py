from flask import Flask, render_template, request, session
from flask import jsonify
# See: https://www.geeksforgeeks.org/how-to-use-flask-session-in-python-flask/
from flask_session import Session

from mcs_interface import MCSInterface

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.before_first_request
def before_first():
    # Because we are using filesystem session, it keeps track of
    # sessions between start ups.  So clear it out when we start.
    [session.pop(key) for key in list(session.keys())]


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
def add():
    # Get the passed key, cleaning it up first
    key = request.data.decode("utf-8")
    if key[0] == '"' and key[len(key) - 1] == '"':
        key = key[1:len(key) - 1]
    # app.logger.warning(f'values in request: {key}')

    mcs_interface = session.get("mcs_interface")

    # We get key presses (w,k, space, etc.).  convert to
    # things the controller understands

    img_name = mcs_interface.perform_action(key)
    resp = jsonify(img_name)
    return resp
