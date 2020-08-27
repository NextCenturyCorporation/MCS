import json
import signal

from contextlib import contextmanager
from .mcs_controller_ai2thor import MCS_Controller_AI2THOR

TIME_LIMIT_SECONDS = 60


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


class MCS:
    """
    Defines utility functions for machine learning modules to create MCS
    controllers and handle config data files.
    """

    """
    Creates and returns a new MCS_Controller object.

    Parameters
    ----------
    unity_app_file_path : str
        The file path to your MCS Unity application.
    debug : boolean, optional

    Returns
    -------
    MCS_Controller
    """
    @staticmethod
    def create_controller(
            unity_app_file_path,
            debug=False,
            enable_noise=False,
            seed=None):
        # TODO: Toggle between AI2-THOR and other controllers like ThreeDWorld?
        try:
            with time_limit(TIME_LIMIT_SECONDS):
                return MCS_Controller_AI2THOR(
                    unity_app_file_path, debug, enable_noise, seed)
        except Exception as Msg:
            print("create_controller() is Hanging. ", Msg)
            return None

    """
    Loads the given JSON config file and returns its data.

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
    @staticmethod
    def load_config_json_file(config_json_file_path):
        try:
            with open(config_json_file_path, encoding='utf-8-sig') \
                    as config_json_file_object:
                try:
                    return json.load(config_json_file_object), None
                except ValueError:
                    return {}, "The given file '" + config_json_file_path + \
                        "' does not contain valid JSON."
        except IOError:
            return {}, "The given file '" + config_json_file_path + \
                "' cannot be found."
