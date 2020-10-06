import json
import signal

from contextlib import contextmanager
from .controller_ai2thor import ControllerAI2THOR

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

    @staticmethod
    def create_controller(unity_app_file_path, debug=False, enable_noise=False,
                          seed=None, size=None, depth_masks=False,
                          object_masks=False, history_enabled=True):
        """
        Creates and returns a new MCS Controller object.

        Parameters
        ----------
        unity_app_file_path : str
            The file path to your MCS Unity application.
        debug : boolean, optional
            Whether to save MCS output debug files in this folder.
            (default False)
        enable_noise : boolean, optional
            Whether to add random noise to the numerical amounts in movement
            and object interaction action parameters.
            (default False)
        seed : int, optional
            A seed for the Python random number generator.
            (default None)
        history_enabled: boolean, optional
            Whether to save all the history files and generated image history to local disk or not.
            (default False)

        Returns
        -------
        Controller
            The MCS Controller object.
        """
        # TODO: Toggle between AI2-THOR and other controllers like ThreeDWorld?
        try:
            with time_limit(TIME_LIMIT_SECONDS):
                return ControllerAI2THOR(unity_app_file_path, debug,
                                         enable_noise, seed, size,
                                         depth_masks, object_masks,
                                         history_enabled)
        except Exception as Msg:
            print("Exception in create_controller()", Msg)
            return None

    @staticmethod
    def load_config_json_file(config_json_file_path):
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
