import json
import logging
import logging.config
import signal
from contextlib import contextmanager
from os.path import exists

from ._version import __version__
from .action import Action
from .config_manager import ConfigManager
from .controller import Controller
from .goal_metadata import GoalCategory, GoalMetadata
from .history_writer import HistoryWriter
from .logging_config import LoggingConfig
from .material import Material
from .object_metadata import ObjectMetadata
from .pose import Pose
from .return_status import ReturnStatus
from .reward import Reward
from .scene_history import SceneHistory
from .serializer import SerializerJson, SerializerMsgPack
from .setup import add_subscribers
from .step_metadata import StepMetadata
from .stringifier import Stringifier
from .unity_executable_provider import UnityExecutableProvider
from .validation import Validation

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


def create_controller(config_file_or_dict=None,
                      unity_app_file_path=None,
                      unity_cache_version=None):
    """
    Creates and returns a new MCS Controller object.

    Parameters
    ----------
    config_file_or_dict: str or dict, required
        Can be a path to configuration file to read in or a dictionary
        of various properties, such as metadata level and whether or
        not to save history files (default None)

        * Note the **order of precedence for config options**, in case more
          than one is given:

        1. **MCS_CONFIG_FILE_PATH** environment variable (meant for internal
           TA2 use during evaluation)
        2. If no environment variable given, use **config_file_or_dict**
           parameter. The value can be a string file path or a dictionary.
        3. Raises FileNotFoundError if no config found.
    unity_app_file_path : str, optional
        The file path to your MCS Unity application.  If Not provided,
        the internal cache and downloader will attempt to locate and use
        the current version.
        (default None)
    unity_cache_version : str, optional
        If no file path is provided for the MCS Unity application, the
        version provided will be found via cache and internal downloader.
        If not provided, the version matching the MCS code will be used.
        (default None)

    Returns
    -------
    Controller
        The MCS Controller object.
    """
    try:
        unity_exec = unity_app_file_path
        if (unity_exec is None):
            unity_provider = UnityExecutableProvider()
            unity_exec = unity_provider.get_executable(
                unity_cache_version).as_posix()

        config = ConfigManager(config_file_or_dict)
        with time_limit(TIME_LIMIT_SECONDS):
            controller = Controller(unity_exec, config)
        if not controller:
            raise Exception('MCS/Python Controller failed to initialize')
        add_subscribers(controller, config)
        return controller
    except Exception as Msg:
        logger.error("Exception in create_controller()", exc_info=Msg)
        return None


def change_config(controller: Controller,
                  config_file_or_dict=None):
    """
    Creates and returns a new MCS Controller object.  Should only be called
    After a run and before a scene is changed.

    Parameters
    ----------
    controller : Controller
        The currently used controller that the config should be changed
        on.
    config_file_or_dict: str or dict, optional
        Can be a path to configuration file to read in or a dictionary
        of various properties, such as metadata level and whether or
        not to save history files (default None)

    """
    config = ConfigManager(config_file_or_dict)
    controller._set_config(config)
    controller.remove_all_event_handlers()
    add_subscribers(controller, config)


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
