from . import import_override  # isort: skip

import concurrent.futures
import json
import logging
import logging.config
import signal
from contextlib import contextmanager
from typing import Dict, Union

import typeguard

from ._version import __version__
from .action import Action
from .config_manager import ConfigManager
from .controller import Controller
from .goal_metadata import GoalCategory, GoalMetadata
from .history_writer import HistoryWriter
from .logging_config import LoggingConfig
from .material import Material
from .object_metadata import ObjectMetadata
from .return_status import ReturnStatus
from .reward import Reward
from .scene_history import SceneHistory
from .serializer import SerializerMsgPack
from .step_metadata import StepMetadata
from .stringifier import Stringifier
from .subscriber import add_subscribers
from .unity_executable_provider import UnityExecutableProvider

logger = logging.getLogger(__name__)
# Set default logging handler to avoid "No handler found" warnings
logger.addHandler(logging.NullHandler())


def get_controller(unity_exec: str, config: ConfigManager):
    """Function to get the controller, pulled into its own
     function so we can time it.  """
    controller = Controller(unity_exec, config)
    return controller


def get_controller_with_timeout(unity_exec: str, config: ConfigManager):
    """Wrapper function that sets a timeout for the controller creation.
    If getting the controller times out, None is returned. """
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future = executor.submit(get_controller, unity_exec, config)
        try:
            controller = future.result(timeout=config.get_controller_timeout())
            return controller
        except concurrent.futures.TimeoutError as Msg:
            logger.error("Timeout error in creating controller", exc_info=Msg)

            # TODO:  Add checks to continue waiting for the controller creation.
            return None


@typeguard.typechecked
def init_logging(log_config: Dict = None,
                 log_config_file: str = "log.config.user.py"):
    """
    Initializes logging system.  If no parameters are provided, a
    default configuration will be applied.  See python logging
    documentation for details.

    https://docs.python.org/3/library/logging.config.html#logging-config-dictschema

    Parameters
    ----------
    log_config : dict, optional
        A dictionary the contains the logging configuration.  If None, a
        default configuration will be used
    log_config_file: str, optional
        Path to an override configuration file.  The file will contain a
        python dictionary for the logging configuration.  This file is
        typically not used, but allows a user to change the logging
        configuration without code changes.  Default, log.config.user.py
    """
    LoggingConfig.init_logging(
        log_config=log_config,
        log_config_file=log_config_file)


@typeguard.typechecked
def create_controller(config_file_or_dict: Union[Dict, str] = None,
                      unity_app_file_path: str = None,
                      unity_cache_version: str = None):
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
        controller = get_controller_with_timeout(unity_exec, config)
        if not controller:
            raise Exception('MCS/Python Controller failed to initialize')
        add_subscribers(controller, config)
        return controller
    except Exception as Msg:
        logger.error("Exception in create_controller()", exc_info=Msg)
        return None


@typeguard.typechecked
def change_config(controller: Controller,
                  config_file_or_dict: Union[Dict, str] = None):
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


@typeguard.typechecked
def load_scene_json_file(scene_json_file_path: str) -> Dict:
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

    Raises
    ------
    FileNotFoundError
    ValueError
    """
    with open(scene_json_file_path, encoding='utf-8-sig') \
            as config_json_file_object:
        return json.load(config_json_file_object)
