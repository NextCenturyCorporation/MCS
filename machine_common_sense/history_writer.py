import json
import os

from time import perf_counter

from .util import Util
from .scene_history import SceneHistory


class HistoryWriter(object):

    HISTORY_DIRECTORY = "SCENE_HISTORY"

    def __init__(self, scene_config_data=None, hist_info={}, timestamp=''):
        self.info_obj = hist_info
        self.current_steps = []  # list of steps in order
        self.end_score = {}
        self.scene_history_file = None
        self.history_obj = {}
        self.last_step_time_millis = perf_counter() * 1000

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

    def write_file(self) -> None:
        if self.scene_history_file:
            with open(self.scene_history_file, "a+") as history_file:
                history_file.write(
                    json.dumps(
                        self.history_obj,
                        cls=HistoryEncoder))

    def filter_history_output(
            self,
            history: SceneHistory) -> SceneHistory:
        """ filter out images from the step history data and
            object lists and action list """
        targets = ['target', 'target_1', 'target2']
        if history.output:
            history.output.action_list = None
            history.output.object_list = None
            history.output.structural_object_list = None
            for target in targets:
                if target in history.output.goal.metadata.keys():
                    if history.output.goal.metadata[target].get(
                            'image', None) is not None:
                        del history.output.goal.metadata[target]['image']
        return history

    def init_timer(self) -> None:
        """Initialize the step timer.  Should be called when first command is
            sent to controller"""
        self.last_step_time_millis = perf_counter() * 1000

    def add_step(self, step_obj: SceneHistory) -> None:
        """Add a new step to the array of history steps"""
        current_time = perf_counter() * 1000
        if step_obj is not None:
            step_obj.delta_time_millis = current_time - \
                self.last_step_time_millis
            self.last_step_time_millis = current_time
            # TODO DW: can we make step a concrete class
            # it was a SceneHistory at one point
            # converted to dict to help with writing to file
            # might be able to handle that another way
            self.current_steps.append(
                # dict(self.filter_history_output(step_obj)))
                vars(step_obj))

    def add_retrospective_report(self, report):
        '''Add retrospective VoE reporting to the history'''
        # TODO maybe loop over the retrospective report?
        # sort by frame number in the history dictionary
        # and add report to that history item
        # or maybe we just pass the whole report and let the class
        # do the loop
        # TODO use writer.current_steps list for reporting
        # TODO maybe add_step should just take in the arguments?
        # use for k, v in report.items() to get sorted results by key
        pass

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
        # TODO DW: wouldn't this be called a flush?
        if not os.path.exists(self.scene_history_file):
            self.write_history_file("", "")

    def __str__(self) -> str:
        return Util.class_to_str(self)


# maybe in the history writer we add a custom json serializer class
class HistoryEncoder(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, 'reprJSON'):
            return o.reprJSON()
        else:
            return json.JSONEncoder.default(self, o)
