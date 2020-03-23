import json

from machine_common_sense.mcs_controller_ai2thor import MCS_Controller_AI2THOR

class MCS:
    """
    Defines utility functions for machine learning modules to create MCS controllers and handle config data files.
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
    def create_controller(unity_app_file_path, debug=False, enable_noise=False):
        # TODO: Toggle between AI2-THOR and other controllers like ThreeDWorld?
        return MCS_Controller_AI2THOR(unity_app_file_path, debug, enable_noise)

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
            with open(config_json_file_path, encoding='utf-8-sig') as config_json_file_object:
                try:
                    return json.load(config_json_file_object), None
                except ValueError:
                    return {}, "The given file '" + config_json_file_path + "' does not contain valid JSON."
        except IOError:
            return {}, "The given file '" + config_json_file_path + "' cannot be found."

