import datetime
import glob
import json
import logging
import os
import sys
import time
from os.path import exists, getctime, relpath

from flask import current_app
from mcs_task_desc import TaskDescription
from PIL import Image
from subprocess_runner import (is_file_open, is_process_running,
                               start_subprocess)

import machine_common_sense as mcs
from machine_common_sense import GoalMetadata

IMG_WIDTH = 600
IMG_HEIGHT = 400
# Use _MEIPASS in the pyinstaller package (frozen=True).
ROOT_PATH = f'{sys._MEIPASS}/' if getattr(sys, 'frozen', False) else ''
RELATIVE_PATH = (
    f'{relpath(ROOT_PATH, os.getcwd())}/'
    # Convert the absolute path used within the pyinstaller package.
    if ROOT_PATH.startswith('/') else ROOT_PATH
)
MCS_INTERFACE_TMP_DIR = 'static/mcsinterface/'
TMP_DIR_FULL_PATH = f'{RELATIVE_PATH}{MCS_INTERFACE_TMP_DIR}'
BLANK_IMAGE_NAME = 'blank_600x400.png'
IMAGE_WAIT_TIMEOUT = 60.0
UNITY_STARTUP_WAIT_TIMEOUT = 10.0
IMAGE_COUNT = 500


def convert_key_to_action(key: str, logger):
    for action in mcs.Action:
        if key.lower() == action.key:
            logger.debug(f"Converting '{key}' into {action.value}")
            return action.value
    logger.debug(f"Unable to convert '{key}'. Returning Pass...")
    return "Pass"


class MCSInterface:
    """We need to have a way to communicate with MCS.  We cannot simply
    create a controller and keep that in the session, because the
    MCS controller object is not easily storable.

    Note, be careful about what you try to put into this class.
    In particular, you cannot include the code from subprocess_runner,
    """

    def __init__(self, user: str):
        self.logger = current_app.logger
        self.logger.debug(f'MCS interface directory: {TMP_DIR_FULL_PATH}')
        self.step_number = 0
        self.scene_id = None
        self.scene_filename = None
        self.step_output = None

        if not exists(TMP_DIR_FULL_PATH):
            os.mkdir(TMP_DIR_FULL_PATH)

        time_str = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
        suffix = f"{time_str}_{user}"
        self.command_out_dir = f"{TMP_DIR_FULL_PATH}cmd_{suffix}"
        self.step_output_dir = f"{TMP_DIR_FULL_PATH}output_{suffix}"
        if not exists(self.command_out_dir):
            os.mkdir(self.command_out_dir)
        if not exists(self.step_output_dir):
            os.mkdir(self.step_output_dir)

        # Make sure that there is a blank image (in case something goes wrong)
        self.blank_path = TMP_DIR_FULL_PATH + BLANK_IMAGE_NAME
        if not exists(self.blank_path):
            img = Image.new('RGB', (IMG_WIDTH, IMG_HEIGHT))
            img.save(self.blank_path)

        # Default to the blank image
        self.img_name = self.blank_path

        # Process id of the unity contoller program
        self.pid = None

    def get_latest_image(self):
        return self.img_name

    def get_latest_step_output(self):
        return self.step_output

    def start_mcs(self):
        # Start the unity controller.  (the function is in a different
        # file so we can pickle / store MCSInterface in the session)
        self.pid = start_subprocess(
            self.command_out_dir,
            self.step_output_dir,
            self.logger.isEnabledFor(logging.DEBUG)
        )

        # Read in the image
        images, _ = self.get_images_and_step_output(startup=True)
        return images

    def is_controller_alive(self):
        # When we re-attach, we need to make sure that the controller
        # still lives, look for it.
        if self.pid is None:
            return False
        return is_process_running(self.pid)

    def load_scene(self, scene_filename: str):
        self.scene_filename = scene_filename
        action_list_str = self.get_action_list()
        goal_info = self.get_goal_info(scene_filename)
        task_desc = self.get_task_desc(scene_filename)
        self.step_number = 0
        self.scene_id = scene_filename[
            (scene_filename.rfind('/') + 1):(scene_filename.rfind('.'))
        ]
        _, images, step_output = self._post_step_and_get_output(scene_filename)
        return images, step_output, action_list_str, goal_info, task_desc

    def perform_action(self, params: object):
        action = None
        if "keypress" in params:
            key = params["keypress"]
            del params["keypress"]
            action = convert_key_to_action(key, self.logger)
        if "action" in params:
            action = params["action"]
            del params["action"]
        full_action, images, step_output = self._post_step_and_get_output(
            action, params)
        if (step_output):
            self.step_number = step_output.get('step_number', self.step_number)
            action_list_str = self.get_action_list(
                step_number=self.step_number)
        return full_action, images, step_output, action_list_str

    def _post_step_and_get_output(self, action: str, params=None):
        full_action_str = action

        image_coord_actions = ["CloseObject", "OpenObject", "PickupObject",
                               "PullObject", "PushObject", "PutObject",
                               "TorqueObject", "RotateObject", "MoveObject",
                               "InteractWithAgent"]

        command_file_name = (
            f'{self.command_out_dir}/command_{self.scene_id}_step_'
            f'{self.step_number}.txt'
        )
        f = open(command_file_name, "a")

        if (action in image_coord_actions and params is not None):
            x_coord = params["objectImageCoordsX"]
            y_coord = params["objectImageCoordsY"]
            if (action != "PutObject"):
                full_action_str += (",objectImageCoordsX=" + str(x_coord) +
                                    ",objectImageCoordsY=" + str(y_coord))
            else:
                full_action_str += (",receptacleObjectImageCoordsX=" +
                                    str(x_coord) +
                                    ",receptacleObjectImageCoordsY=" +
                                    str(y_coord))

            if (action in ["OpenObject", "CloseObject"] and
                    "amount" in params):
                amount = params["amount"]
                full_action_str += (",amount=" + str(amount))

            if (action in ["PullObject", "PushObject", "TorqueObject"] and
                    "force" in params):
                force = params["force"]
                full_action_str += (",force=" + str(force))

            if (action == "RotateObject" and
                    "clockwise" in params):
                clockwise = params["clockwise"]
                full_action_str += (",clockwise=" + str(clockwise))

            if (action == "MoveObject"):
                if ("lateral" in params):
                    lateral = params["lateral"]
                    full_action_str += (",lateral=" + str(lateral))
                if ("straight" in params):
                    straight = params["straight"]
                    full_action_str += (",straight=" + str(straight))

        f.write(full_action_str)
        f.close()
        # wait for action to process
        time.sleep(0.5)

        action_to_return = full_action_str

        is_initialize = action_to_return.endswith("json")

        if is_initialize:
            action_to_return = self.scene_id

        images, step_output = self.get_images_and_step_output(
            init_scene=is_initialize)

        return action_to_return, images, step_output

    def check_for_error(self, elapsed):
        # Shouldn't need to wait very long for errors like "invalid action"
        secs_to_check = 1.0
        if (elapsed > secs_to_check):
            error_file_list = glob.glob(
                self.step_output_dir + "/error_*.json")

            return len(error_file_list) > 0

    def get_images_and_step_output(self, startup=False, init_scene=False):
        """Watch the output directory and return the latest images and step
        output that appears. If it does not appear in <timeout> seconds, then
        give up and return a blank image."""
        timestart = time.time()

        while True:
            timenow = time.time()
            elapsed = (timenow - timestart)
            if (startup and elapsed > UNITY_STARTUP_WAIT_TIMEOUT):
                self.logger.debug(
                    "Display blank image on default when starting up.")
                self.img_name = self.blank_path
                return [self.img_name], self.step_output

            quick_error_check = self.check_for_error(elapsed)

            if elapsed > IMAGE_WAIT_TIMEOUT or quick_error_check:
                log_message = "Timeout waiting for image"
                if (quick_error_check):
                    log_message = "Error returned from MCS controller."

                self.logger.warn(log_message)

                list_of_error_files = glob.glob(
                    self.step_output_dir + "/error_*.json")

                if len(list_of_error_files) > 0:
                    latest_error_file = max(
                        list_of_error_files, key=getctime
                    )
                    if latest_error_file.endswith(
                            f"step_{self.step_number}.json") or init_scene:
                        opened_error_file = open(latest_error_file, "r")
                        new_error_output = json.load(opened_error_file)
                        opened_error_file.close()
                        if (self.img_name is None):
                            self.img_name = self.blank_path
                        if (self.step_output is None):
                            self.step_output = {}

                        self.step_output['error_output'] = {
                            'step_number': new_error_output["step_number"],
                            'error': new_error_output["error"]
                        }

                return [self.img_name], self.step_output

            # Sort descending by date/time modified (newest first)
            list_of_output_files = list(reversed(sorted(
                glob.glob(self.step_output_dir + "/step_output_*.json"),
                key=getctime
            )))
            list_of_img_files = list(reversed(sorted(
                glob.glob(self.step_output_dir + "/rgb_*.png"),
                key=getctime
            )))

            # Image file logic
            if len(list_of_img_files) > 0 and len(list_of_output_files) > 0:
                latest_json_file = list_of_output_files[0]

                # Keep only the latest output file.
                for file in list_of_output_files[1:]:
                    os.unlink(file)

                latest_image_file = list_of_img_files[0]

                # Keep only the latest image files. Use step_number if less
                # than IMAGE_COUNT to remove images from previous scenes.
                image_count = min(IMAGE_COUNT, self.step_number + 2)
                for file in list_of_img_files[image_count:]:
                    os.unlink(file)

                # wait to make sure we've finished loading the new image
                # (not sure why the is_file_open check below didn't
                # do the trick?)
                time.sleep(0.1)

                # Check to see if the unity controller still has the file open
                for x in range(0, 100):
                    if (is_file_open(self.pid, latest_image_file) or
                            is_file_open(self.pid, latest_json_file)):
                        time.sleep(0.03)
                    else:
                        break

                opened_json_file = open(latest_json_file, "r")
                new_step_output = json.load(opened_json_file)
                opened_json_file.close()

                has_new_step_output = (("step_number" in new_step_output and
                                        (self.step_output is None or
                                         self.step_number == 0)) or
                                       ("step_number" in self.step_output and
                                       new_step_output["step_number"] >
                                       self.step_output["step_number"]))

                if latest_image_file != self.img_name and has_new_step_output:
                    self.step_output = new_step_output
                    self.img_name = latest_image_file
                    return list_of_img_files[:image_count], self.step_output

            time.sleep(0.05)

    def get_scene_list(self):
        '''Look in scenes/ and get a list of all the scenes'''
        scene_list = []
        scene_dir = 'scenes/'
        for scene in os.listdir(scene_dir):
            if scene.endswith(".json"):
                scene_list.append(scene)

        scene_list.sort()
        return scene_list

    def get_action_list(self, step_number=0):
        """Simplification of getting the action list as a function
        of step"""
        is_passive = False
        actions = GoalMetadata.DEFAULT_ACTIONS
        try:
            with open(self.scene_filename, 'r') as scene_file:
                scene_data = json.load(scene_file)
                if 'goal' in scene_data:
                    goal = scene_data['goal']
                    if 'category' in goal:
                        is_passive = goal['category'] in [
                            'agents',
                            'intuitive_physics',
                            'passive'
                        ]
                    if is_passive:
                        actions = GoalMetadata.DEFAULT_PASSIVE_SCENE_ACTIONS
                    if len(goal.get('action_list', [])) > step_number:
                        actions = goal['action_list'][step_number]
                    return self.simplify_action_list(actions)
        except Exception:
            self.logger.exception(
                "Exception in reading actions from json file")
            return self.simplify_action_list(actions)

    def get_goal_info(self, scene_filename):
        """Obtain the goal info from a scene."""
        try:
            with open(scene_filename, 'r') as scene_file:
                scene_data = json.load(scene_file)
                if 'goal' in scene_data:
                    return scene_data['goal']
        except Exception:
            self.logger.exception("Exception in reading goal from json file")
            return {}

    def get_task_desc(self, scene_filename):
        """Get task description based on filename from mcs_task_desc.py"""
        self.logger.debug(
            f"Attempt to get task description based"
            f"on scene_filename: {scene_filename}")
        scene_type = scene_filename.split('/')[-1].split('0')[0][:-1].upper()
        # Remove "eval_7_" from the scene name if it's present.
        scene_type = scene_type.replace('eval_7_', '')
        # Rename passive_agents to passive_agent for simplicity, because I'm
        # apparently inconsistent with our naming conventions (sorry).
        scene_type = scene_type.replace('passive_agents_', 'passive_agent_')

        for description in TaskDescription:
            if (description.name == scene_type):
                self.logger.debug(
                    f"Scene type identified: {description.name}")
                return description.value

        self.logger.warn(f"Scene type {scene_type} not found, returning 'N/A'")
        return "N/A"

    def get_controller_pid(self):
        return self.pid

    def simplify_action_list(self, default_action_list):
        """The action list looks something like:
        [('CloseObject', {}), ('DropObject', {}), ('MoveAhead', {}), ...
        which is not very user-friendly.  For each of them, remove
        the extra quotes"""
        actions = []
        if default_action_list is not None and len(default_action_list) > 0:
            for action_pair in default_action_list:
                if isinstance(action_pair, tuple) and len(action_pair) > 0:
                    actions.append(action_pair[0])
                else:
                    actions.append(action_pair)
        return ", ".join(actions)
