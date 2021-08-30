import json
import logging
import os
import pathlib
from time import perf_counter
from typing import Dict

from .controller_events import AbstractControllerSubscriber
from .scene_history import SceneHistory
from .stringifier import Stringifier

logger = logging.getLogger(__name__)


class HistoryEventHandler(AbstractControllerSubscriber):

    def __init__(self):
        AbstractControllerSubscriber.__init__(self)
        self.__history_writer = None
        self.__history_item = None

    def on_start_scene(self, payload):
        if payload.config.is_history_enabled():

            # Ensure the previous scene history writer has saved its file.
            if self.__history_writer:
                self.__history_writer.check_file_written()

            hist_info = {}
            hist_info[
                payload.config.CONFIG_EVALUATION_NAME
            ] = payload.config.get_evaluation_name()
            hist_info[
                payload.config.CONFIG_METADATA_TIER
            ] = payload.config.get_metadata_tier()
            hist_info[
                payload.config.CONFIG_TEAM
            ] = payload.config.get_team()

            # Create a new scene history writer with each new scene (config
            # data) so we always create a new, separate scene history file.
            self.__history_writer = HistoryWriter(payload.scene_config,
                                                  hist_info,
                                                  payload.timestamp)

    def on_before_step(self, payload):
        if payload.config.is_history_enabled():
            if payload.step_number == 0:
                self.__history_writer.init_timer()
            if payload.step_number > 0:
                self.__history_writer.add_step(self.__history_item)

    def on_after_step(self, payload):
        output = payload.step_output.copy_without_depth_or_images()

        self.__history_item = SceneHistory(
            step=payload.step_number,
            action=payload.ai2thor_action,
            args=payload.action_kwargs,
            params=payload.step_params,
            output=output,
            delta_time_millis=0)

    def on_prediction(self, payload):
        # add history step prediction attributes before add to the writer
        # in the next step
        if self.__history_item is not None:
            self.__history_item.classification = payload.choice
            self.__history_item.confidence = payload.confidence
            self.__history_item.violations_xy_list = payload.violations_xy_list
            self.__history_item.internal_state = payload.internal_state

    def on_end_scene(self, payload):
        if (
            self.__history_writer is not None and
            payload.config.is_history_enabled()
        ):
            self.__history_writer.add_step(self.__history_item)

            # Loop back and fill out previous steps with
            # retrospective report
            # TODO: MCS-513: Kept the same property names as before.
            # Did we want to rename any of these properties?
            # If so we will need to update ingest.
            for step in self.__history_writer.current_steps:
                currentStep = step.get("step")

                findStepInReport = payload.report.get(currentStep)

                if(findStepInReport is not None):
                    step["classification"] = findStepInReport.get("choice")
                    step["confidence"] = findStepInReport.get(
                        "classification")
                    step["violations_xy_list"] = findStepInReport.get(
                        "violations_xy_list")
                    step["internal_state"] = findStepInReport.get(
                        "internal_state")

            self.__history_writer.write_history_file(
                payload.choice, payload.confidence)

    def _get_filename_without_timestamp(self, filepath: pathlib.Path):
        return filepath.stem[:-16] + filepath.suffix


class HistoryWriter(object):

    HISTORY_DIRECTORY = "SCENE_HISTORY"

    def __init__(self, scene_config_data=None, hist_info={}, timestamp=''):
        self.info_obj = hist_info
        self.current_steps = []
        self.end_score = {}
        self.scene_history_file = None
        self.history_obj = {}
        self.last_step_time_millis = perf_counter() * 1000

        if not os.path.exists(self.HISTORY_DIRECTORY):
            logger.debug(f"Making history directory {self.HISTORY_DIRECTORY}")
            os.makedirs(self.HISTORY_DIRECTORY)

        scene_name = scene_config_data.name
        prefix_directory = None
        if '/' in scene_name:
            prefix, scene_basename = scene_name.rsplit('/', 1)
            prefix_directory = os.path.join(self.HISTORY_DIRECTORY, prefix)
            if not os.path.exists(prefix_directory):
                logger.debug(f"Making prefix directory {prefix_directory}")
                os.makedirs(prefix_directory)

        if (not scene_config_data.screenshot):
            self.scene_history_file = os.path.join(
                self.HISTORY_DIRECTORY, scene_config_data.name.replace(
                    '.json', '') + "-" + timestamp + ".json")

        self.info_obj['name'] = scene_config_data.name.replace(
            '.json', '')
        self.info_obj['timestamp'] = timestamp

    def write_file(self):
        if self.scene_history_file:
            logger.info(f"Saving history file {self.scene_history_file}")
            with open(self.scene_history_file, "a+") as history_file:
                history_file.write(json.dumps(self.history_obj))

    def filter_history_output(
            self,
            history: SceneHistory) -> SceneHistory:
        """ filter out images from the step history data and
            object lists and action list """
        if history.output:
            history.output.action_list = None
            history.output.object_list = None
            history.output.structural_object_list = None
            targets = ['target', 'target_1', 'target2']
            for target in targets:
                if (
                    target in history.output.goal.metadata.keys() and
                    history.output.goal.metadata[target].get('image', None)
                    is not None
                ):
                    del history.output.goal.metadata[target]['image']
        return history

    def init_timer(self):
        """Initialize the step timer.  Should be called when first command is
            sent to controller"""
        self.last_step_time_millis = perf_counter() * 1000

    def add_step(self, step_obj: Dict):
        """Add a new step to the array of history steps"""
        current_time = perf_counter() * 1000
        if step_obj is not None:
            step_obj.delta_time_millis = current_time - \
                self.last_step_time_millis
            self.last_step_time_millis = current_time
            logger.debug("Adding history step")
            self.current_steps.append(
                dict(self.filter_history_output(step_obj)))

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
        return Stringifier.class_to_str(self)
