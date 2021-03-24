import json
import signal

from contextlib import contextmanager

from .action import Action
from .controller import Controller
from .goal_metadata import GoalMetadata, GoalCategory
from .material import Material
from .object_metadata import ObjectMetadata
from .pose import Pose
from .return_status import ReturnStatus
from .reward import Reward
from .scene_history import SceneHistory
from .history_writer import HistoryWriter
from .step_metadata import StepMetadata
from .util import Util
from .getchHelper import getch
from .serializer import SerializerMsgPack, SerializerJson
from ._version import __version__


# Timeout at 3 minutes (180 seconds).  It was 60 seconds but
# this can cause timeouts on EC2 instances
TIME_LIMIT_SECONDS = 180


@contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise Exception("Time out!")
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)


def create_controller(unity_app_file_path,
                      config_file_path=None):
    """
    Creates and returns a new MCS Controller object.

    Parameters
    ----------
    unity_app_file_path : str
        The file path to your MCS Unity application.
    config_file_path: str, optional
        Path to configuration file to read in and set various properties,
        such as metadata level and whether or not to save history files
        (default None)

    Returns
    -------
    Controller
        The MCS Controller object.
    """
    try:
        with time_limit(TIME_LIMIT_SECONDS):
            return Controller(unity_app_file_path,
                              config_file_path)
    except Exception as Msg:
        print("Exception in create_controller()", Msg)
        return None


def load_scene_json_file(scene_json_file_path):
    """
    Loads the given JSON scene config file and returns its data.

    Parameters
    ----------
    config_json_file_path : str
        The file path to your MCS JSON scene configuration file.

    Returns
    -------
    dict
        The MCS scene configuration data from the given JSON file.
    None or string
        The error status (if any).
    """
    try:
        with open(scene_json_file_path, encoding='utf-8-sig') \
                as config_json_file_object:
            try:
                return json.load(config_json_file_object), None
            except ValueError:
                return {}, "The given file '" + scene_json_file_path + \
                    "' does not contain valid JSON."
    except IOError:
        return {}, "The given file '" + scene_json_file_path + \
            "' cannot be found."
