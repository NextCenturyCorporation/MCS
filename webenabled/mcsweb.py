import logging
import psutil
import random
import string

from flask import (Flask, jsonify, make_response, render_template, request,
                   session)
# See: https://www.geeksforgeeks.org/how-to-use-flask-session-in-python-flask/
from flask_session import Session
from mcs_interface import MCSInterface
from webenabled_common import LOG_CONFIG

# Configure logging _before_ creating the app oject
# https://flask.palletsprojects.com/en/2.0.x/logging/
logging.config.dictConfig(LOG_CONFIG)

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


def clean_request_data(request, is_json=False):
    """When we get a response from the client, it can be a mess
    and wrapped in weird ways.  Clean it up."""

    if not is_json:
        # Request data comes as binary, convert to text
        data = request.data.decode("utf-8")

        # Request data has quotes around it, remove them.
        if data[0] == '"' and data[len(data) - 1] == '"':
            data = data[1:len(data) - 1]

    else:
        # Read data as json
        data = request.get_json(cache=False)

        for key in data:
            value = data[key]
            # remove any extra quotes from strings
            if isinstance(value, str) and value[0] == '"' and value[len(
                    value) - 1] == '"':
                value = value[1:len(value) - 1]
                data[key] = value

    return data


def get_mcs_interface(request, label):
    # Do we know who this is?
    uniq_id_str = request.cookies.get("uniq_id")

    # If old user, get stored mcs interface
    if uniq_id_str is not None:
        app.logger.info(f"{label}: existing user: {uniq_id_str}")
        mcs_interface = session.get(uniq_id_str)
        if mcs_interface is not None:
            controller_alive = mcs_interface.is_controller_alive()
            if controller_alive:
                return mcs_interface, uniq_id_str
            app.logger.info("MCS controller is unavailable")
        else:
            app.logger.info("MCS interface is unavailable")

    letters = string.ascii_lowercase
    uniq_id_str = ''.join(random.choice(letters) for i in range(10))
    app.logger.info(f"{label}: new user: {uniq_id_str}")

    # Don't recognize, create new mcs interface
    mcs_interface = MCSInterface(uniq_id_str)
    mcs_interface.start_mcs()
    session[uniq_id_str] = mcs_interface

    return mcs_interface, uniq_id_str


@app.route('/mcs')
def show_mcs_page():
    app.logger.info("=" * 30)
    app.logger.info(
        "Initialize page before checking for "
        "controller and existing user session...")
    rendered_template = render_template(
        'mcs_page.html',
        unityimg="static/blank_600x400.png",
        scene_list=[])
    resp = make_response(rendered_template)

    return resp


@app.route('/load_controller', methods=["POST"])
def handle_load_controller():
    app.logger.info("=" * 30)
    mcs_interface, uniq_id_str = get_mcs_interface(request, "Load page")
    if mcs_interface is None:
        app.logger.warn("Cannot load MCS interface")
        return

    img = mcs_interface.blank_path
    scene_list = mcs_interface.get_scene_list()

    resp = jsonify(image=img, scene_list=scene_list)

    resp.set_cookie("uniq_id", uniq_id_str)

    return resp


@app.route("/keypress", methods=["POST"])
def handle_keypress():
    app.logger.info("=" * 30)
    mcs_interface, _ = get_mcs_interface(request, "Key press")
    if mcs_interface is None:
        app.logger.warn("Cannot load MCS interface")
        return

    params = clean_request_data(request, is_json=True)
    key = params["keypress"]
    action_string, img, step_output, action_list = mcs_interface.perform_action(params)  # noqa: E501
    step_number = mcs_interface.step_number
    app.logger.info(
        f"Key press: '{key}', action string: {action_string}, "
        f"step {step_number}, img: {img}, output: {step_output}")
    resp = jsonify(
        last_action=action_string,
        action_list=action_list,
        image=img,
        step=step_number,
        step_output=step_output)
    return resp


@app.route("/exit_unity", methods=["POST"])
def exit_unity():
    app.logger.info("=" * 30)
    mcs_interface, unique_id = get_mcs_interface(request, "Exit Unity")
    if mcs_interface is None:
        app.logger.warn("Cannot load MCS interface")
        return

    controller_pid = mcs_interface.get_controller_pid()

    app.logger.info(
        "Attempting to clean up processes after browser has been closed.")

    for p in psutil.process_iter(['pid']):
        if p.info['pid'] == controller_pid:
            children = p.children(recursive=True)
            for c_process in children:
                app.logger.info(
                    f"Found child process of controller: {c_process}, "
                    f"will attempt to end.")
                c_process.kill()

            app.logger.info(
                f"Found controller process: {p}, will attempt to end.")
            p.kill()

    if (unique_id is None):
        unique_id = request.cookies.get("uniq_id")

    app.logger.info(
        f"Clear user session for: {unique_id}")
    del session[unique_id]

    resp = jsonify(
        ended_controller_process=controller_pid,
        ended_session=unique_id
    )
    resp.delete_cookie('uniq_id')

    return resp


@app.route("/scene_selection", methods=["POST"])
def handle_scene_selection():
    app.logger.info("=" * 30)
    mcs_interface, _ = get_mcs_interface(request, "Start scene")
    if mcs_interface is None:
        app.logger.warn("Cannot load MCS interface")
        return

    # Get the scene filename and tell interface to load it.
    scene_filename = clean_request_data(request)
    img, step_output, action_list, goal_info = mcs_interface.load_scene(
        "scenes/" + scene_filename)
    app.logger.info(f"Start scene: {scene_filename}, output: {img}")
    resp = jsonify(
        last_action="Initialize",
        action_list=action_list,
        image=img,
        scene=scene_filename,
        goal=goal_info,
        step=0,
        step_output=step_output
    )
    return resp
