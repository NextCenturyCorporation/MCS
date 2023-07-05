import datetime
import glob
import json
import os
import time
from os.path import exists

from flask import current_app
from PIL import Image
from subprocess_runner import (is_file_open, is_process_running,
                               start_subprocess)

import machine_common_sense as mcs
from machine_common_sense import GoalMetadata

IMG_WIDTH = 600
IMG_HEIGHT = 400
MCS_INTERFACE_TMP_DIR = "static/mcsinterface/"
BLANK_IMAGE_NAME = 'blank_600x400.png'
IMAGE_WAIT_TIMEOUT = 20.0


def convert_key_to_action(key: str, logger):
    for action in mcs.Action:
        if key == action.key:
            logger.info(f"Converting '{key}' into {action.value}")
            return action.value
    logger.info(f"Unable to convert '{key}'. Returning Pass...")
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
        # TODO FIXME Use the step number from the output metadata.
        self.step_number = 0
        self.scene_id = None

        if not exists(MCS_INTERFACE_TMP_DIR):
            os.mkdir(MCS_INTERFACE_TMP_DIR)

        time_str = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
        suffix = f"{time_str}_{user}"
        self.command_out_dir = f"{MCS_INTERFACE_TMP_DIR}cmd_{suffix}"
        self.image_in_dir = f"{MCS_INTERFACE_TMP_DIR}img_{suffix}"
        if not exists(self.command_out_dir):
            os.mkdir(self.command_out_dir)
        if not exists(self.image_in_dir):
            os.mkdir(self.image_in_dir)

        # Make sure that there is a blank image (in case something goes wrong)
        self.blank_path = MCS_INTERFACE_TMP_DIR + BLANK_IMAGE_NAME
        if not exists(self.blank_path):
            img = Image.new('RGB', (IMG_WIDTH, IMG_HEIGHT))
            img.save(self.blank_path)

        # Default to the blank image
        self.img_name = self.blank_path

        # Process id of the unity contoller program
        self.pid = None

    def get_latest_image(self):
        return self.img_name

    def start_mcs(self):
        # Start the unity controller.  (the function is in a different
        # file so we can pickle / store MCSInterface in the session)
        self.pid = start_subprocess(self.command_out_dir, self.image_in_dir)

        # Read in the image
        self.img_name = self.get_image_name()
        return self.img_name

    def is_controller_alive(self):
        # When we re-attach, we need to make sure that the controller
        # still lives, look for it.
        if self.pid is None:
            return False
        return is_process_running(self.pid)

    def load_scene(self, scene_filename: str):
        action_list_str = self.get_action_list(scene_filename)
        self.step_number = 0
        self.scene_id = scene_filename[
            (scene_filename.rfind('/') + 1):(scene_filename.rfind('.'))
        ]
        img = self._post_step_and_get_image(scene_filename)
        return img, action_list_str

    def perform_action(self, key: str):
        action = convert_key_to_action(key, self.logger)
        self.step_number = self.step_number + 1
        return self._post_step_and_get_image(action)

    def _post_step_and_get_image(self, action):
        command_file_name = (
            f'{self.command_out_dir}/command_{self.scene_id}_step_'
            f'{self.step_number}.txt'
        )
        f = open(command_file_name, "a")
        f.write(action)
        f.close()
        # wait for action to process
        time.sleep(0.1)
        return self.get_image_name()

    def get_image_name(self):
        """Watch the output directory, get image that appears.  If it does
        not appear in timeout seconds, give up and return blank."""
        timestart = time.time()

        while True:
            timenow = time.time()
            elapsed = (timenow - timestart)
            if elapsed > IMAGE_WAIT_TIMEOUT:
                self.logger.info("Timeout waiting for image")
                self.img_name = self.blank_path
                return self.img_name

            list_of_files = glob.glob(self.image_in_dir + "/rgb_*.png")
            if len(list_of_files) > 0:
                latest_file = max(list_of_files, key=os.path.getctime)

                # Remove old files?  Probably a good idea, keep disk usage down
                for file in list_of_files:
                    if file != latest_file:
                        os.unlink(file)

                # wait to make sure we've finished loading the new image
                # (not sure why the is_file_open check below didn't
                # do the trick?)
                time.sleep(0.1)

                # Check to see if the unity controller still has the file open
                for x in range(0, 100):
                    if is_file_open(self.pid, latest_file):
                        time.sleep(0.01)
                    else:
                        break

                if latest_file != self.img_name:
                    self.img_name = latest_file
                    return self.img_name

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

    def get_action_list(self, scene_filename):
        """Simplification of getting the action list as a function
        of step"""
        is_passive = False
        actions = GoalMetadata.DEFAULT_ACTIONS
        try:
            with open(scene_filename, 'r') as scene_file:
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
                    if goal.get('action_list'):
                        actions = goal['action_list'][0]
                    return self.simplify_action_list(scene_filename, actions)
        except Exception:
            self.logger.exception("Exception in reading json file")
            return self.simplify_action_list(scene_filename, actions)

    def simplify_action_list(self, scene_filename, default_action_list):
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
