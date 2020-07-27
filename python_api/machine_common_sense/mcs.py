import json

from .mcs_controller_ai2thor import MCS_Controller_AI2THOR

class MCS:
    """
    Defines utility functions for machine learning modules to create MCS controllers and handle config data files.
    """

    @staticmethod
    def create_controller(unity_app_file_path, debug=False, enable_noise=False, seed=None):
        """
            **static create_controller(unity_app_file_path)**
            Creates and returns an MCS Controller object using the Unity application at the given file path.

            :param unity_app_file_path : The file path to the MCS Unity application. The TA2 team will give you this application.
            :type unity_app_file_path: string
            :return: The MCS controller object.
            :type: MCS_Controller
        """
        # TODO: Toggle between AI2-THOR and other controllers like ThreeDWorld?
        return MCS_Controller_AI2THOR(unity_app_file_path, debug, enable_noise, seed)

    @staticmethod
    def load_config_json_file(config_json_file_path):
        """
            **Loads the given JSON config file and returns its data.**
            :param config_json_file_path : The file path to the MCS scene configuration JSON file. The TA2 team will give you these files, or you can make them yourself (more details on how to do this are coming soon).
            :type config_json_file_path: string
            :return config_data: The MCS scene configuration data object
            :type: dict
        """
        try:
            with open(config_json_file_path, encoding='utf-8-sig') as config_json_file_object:
                try:
                    return json.load(config_json_file_object), None
                except ValueError:
                    return {}, "The given file '" + config_json_file_path + "' does not contain valid JSON."
        except IOError:
            return {}, "The given file '" + config_json_file_path + "' cannot be found."

