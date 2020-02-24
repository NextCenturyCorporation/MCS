import json
from mcs_controller_ai2thor import MCS_Controller_AI2THOR

class MCS:

    """
    Creates and returns a new MCS_Controller object.

    Parameters
    ----------
    unity_app_file_path : str
        File path to your Unity app.

    Returns
    -------
    MCS_Controller
    """
    @staticmethod
    def create_controller(unity_app_file_path):
        # TODO: Toggle between AI2-THOR and other controllers like ThreeDWorld?
        return MCS_Controller_AI2THOR(unity_app_file_path)

    """
    Loads the given JSON config file and returns its data.

    Parameters
    ----------
    config_json_file_path : str
        File path to your JSON file.

    Returns
    -------
    dict
        The data from the JSON file.
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

