import logging
import logging.config
from os.path import exists
import json
import signal

from contextlib import contextmanager

from .action import Action
from .config_manager import ConfigManager
from .controller import Controller
from .controller_logger import ControllerAi2thorFileGenerator
from .controller_logger import ControllerDebugFileGenerator
from .controller_logger import ControllerLogger
from .controller_video_manager import ControllerVideoManager
from .goal_metadata import GoalMetadata, GoalCategory
from .logging_config import LoggingConfig
from .material import Material
from .validation import Validation
from .object_metadata import ObjectMetadata
from .pose import Pose
from .return_status import ReturnStatus
from .reward import Reward
from .scene_history import SceneHistory
from .history_writer import HistoryEventHandler, HistoryWriter
from .step_metadata import StepMetadata
from .serializer import SerializerMsgPack, SerializerJson
from .stringifier import Stringifier
from ._version import __version__


logger = logging.getLogger(__name__)
# Set default logging handler to avoid "No handler found" warnings
logger.addHandler(logging.NullHandler())

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


def init_logging(log_config=None,
                 log_config_file="log.config.user.py"):
    """
    Initializes logging system.  If no parameters are provided, a
    default configuration will be applied.  See python logging
    documentation for details.

    https://docs.python.org/3/library/logging.config.html#logging-config-dictschema

    Parameters
    ----------
    log_config : dict, optional
        A dictionary the contains the logging configuration.  If None, a default configuration
        will be used
    log_config_file: str, optional
        Path to an override configuration file.  The file will contain a python dictionary
        for the logging configuration.  This file is typically not used, but allows a user
        to change the logging configuration without code changes.  Default, log.config.user.py
    """
    LoggingConfig.init_logging(
        log_config=log_config,
        log_config_file=log_config_file)


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
        config = ConfigManager(config_file_path)
        with time_limit(TIME_LIMIT_SECONDS):
            controller = Controller(unity_app_file_path,
                                    config)
        _add_subscribers(controller, config)
        return controller
    except Exception as Msg:
        logger.error("Exception in create_controller()", exc_info=Msg)
        return None


def _add_subscribers(controller: Controller, config: ConfigManager):
    if controller:
        if config.is_save_debug_json():
            controller.subscribe(ControllerDebugFileGenerator())
            controller.subscribe(ControllerAi2thorFileGenerator())
        # TODO MCS-664 Once separated, use config to only subscribe when,
        # # necessary
        controller.subscribe(ControllerVideoManager())
        controller.subscribe(ControllerLogger())
        # TODO once we remove evaulation code, we can better handle when,
        # this handler subscribes
        controller.subscribe(HistoryEventHandler())


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
