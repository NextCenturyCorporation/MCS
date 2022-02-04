import glob
import os
import time
import uuid
from os.path import exists

import machine_common_sense as mcs
from PIL import Image

from subprocess_runner import start_subprocess, is_file_open

IMG_WIDTH = 640
IMG_HEIGHT = 480
MCS_INTERFACE_TMP_DIR = "static/mcsinterface/"
BLANK_IMAGE_NAME = 'blank_640x480.png'


def convert_key_to_action(key: str):
    for action in mcs.Action:
        # print(f"action {action}  {action.key}")
        if key == action.key:
            return action.value

    print(f"Do not recognize:  {key}.  Returning pass")
    return "Pass"


class MCSInterface:
    """We need to have a way to communicate with MCS.  We cannot simply
    create a controller and keep that in the session, because the
    MCS controller object is not easily storable.  """

    def __init__(self):
        if not exists(MCS_INTERFACE_TMP_DIR):
            os.mkdir(MCS_INTERFACE_TMP_DIR)

        self.command_out_dir = MCS_INTERFACE_TMP_DIR + "cmd_" + str(time.time()) + "/"
        self.image_in_dir = MCS_INTERFACE_TMP_DIR + "img" + str(time.time()) + "/"
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

    def load_scene(self, scene_filename: str):
        print(f" loading {scene_filename}")
        img = self._post_step_and_get_image(scene_filename)
        print(f" ----- done loading scene. image is {img} ")
        # img = self.perform_action(" ")
        # print(f" finished action pass {img}")
        return img

    def perform_action(self, key: str):
        action = convert_key_to_action(key)
        return self._post_step_and_get_image(action)

    def _post_step_and_get_image(self, action):
        command_file_name = self.command_out_dir + "command_" + str(uuid.uuid4()) + ".txt"
        f = open(command_file_name, "a")
        f.write(action)
        f.close()
        return self.get_image_name()

    def get_image_name(self):
        """Watch the output directory, get image that appears.  If it does
        not appear in 3 seconds, give up and return blank."""
        timestart = time.time()

        while True:
            timenow = time.time()
            elapsed = (timenow - timestart)
            # print(f"elapsed {elapsed}")
            if elapsed > 3.:
                print("timeout, returning blank")
                return self.blank_path

            list_of_files = glob.glob(self.image_in_dir + "*.png")
            if len(list_of_files) > 0:
                latest_file = max(list_of_files, key=os.path.getctime)

                # Remove old files?  Probably a good idea, keep disk usage down
                for file in list_of_files:
                    if file != latest_file:
                        os.unlink(file)

                # Check to see if the unity controller still has the file open
                for x in range(0, 100):
                    if is_file_open(self.pid, latest_file):
                        time.sleep(0.01)
                    else:
                        break

                print(f"Returning from interface: {latest_file}")
                self.img_name = latest_file
                return latest_file

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
