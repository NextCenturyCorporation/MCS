from .util import Util
from .scene_history import SceneHistory
from typing import Dict
import json
import os
import datetime


class HistoryWriter(object):
    def __init__(self, scene_config_data=None, hist_info={}, timestamp=''):
        self.info_obj = hist_info
        self.current_steps = []
        self.end_score = {}
        self.scene_history_file = None
        self.history_obj = {}
        self.HISTORY_DIRECTORY = "SCENE_HISTORY"

        if not os.path.exists(self.HISTORY_DIRECTORY):
            os.makedirs(self.HISTORY_DIRECTORY)

        scene_name = scene_config_data['name']
        prefix_directory = None
        if '/' in scene_name:
            prefix, scene_basename = scene_name.rsplit('/', 1)
            print(f"{prefix} {scene_basename}")
            prefix_directory = os.path.join(self.HISTORY_DIRECTORY, prefix)
            if not os.path.exists(prefix_directory):
                os.makedirs(prefix_directory)

        if ('screenshot' not in scene_config_data or
                not scene_config_data['screenshot']):
            self.scene_history_file = os.path.join(
                self.HISTORY_DIRECTORY, scene_config_data['name'].replace(
                    '.json', '') + "-" + timestamp + ".json")

        self.info_obj['name'] = scene_config_data['name'].replace(
            '.json', '')
        self.info_obj['timestamp'] = timestamp

    def generate_time(self):
        return datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    def write_file(self):
        if self.scene_history_file:
            with open(self.scene_history_file, "a+") as history_file:
                history_file.write(json.dumps(
                    self.history_obj, indent=4))

    def filter_history_images(
            self,
            history: SceneHistory) -> SceneHistory:
        """ filter out images from the step history data"""
        targets = ['target', 'target_1', 'target2']
        if history.output:
            for target in targets:
                if target in history.output.goal.metadata.keys():
                    if history.output.goal.metadata[target].get(
                            'image', None) is not None:
                        del history.output.goal.metadata[target]['image']
        return history

    def add_step(self, step_obj: Dict):
        """ Add a new step to the array of history steps"""
        if step_obj is not None:
            self.current_steps.append(
                dict(self.filter_history_images(step_obj)))

    def write_history_file(self, classification, confidence):
        """ Add the end score obj, create the object
            that will be written to file"""
        self.end_score["classification"] = classification
        self.end_score["confidence"] = str(confidence)

        self.history_obj["info"] = self.info_obj
        self.history_obj["steps"] = self.current_steps
        self.history_obj["score"] = self.end_score

        self.write_file()

    def check_file_written(self):
        """ Will check to see if the file has been written, if not,
            it will write out what is currently in the history object"""
        if not os.path.exists(self.scene_history_file):
            self.write_history_file("", "")

    def __str__(self):
        return Util.class_to_str(self)
