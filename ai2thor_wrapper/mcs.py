import json
from mcs_controller_ai2thor import MCS_Controller_AI2THOR

class MCS:

    @staticmethod
    def create_controller(unity_app_file_path):
        # TODO: Toggle between AI2-THOR and other controllers like ThreeDWorld?
        return MCS_Controller_AI2THOR(unity_app_file_path)

    @staticmethod
    def load_config_json_file(config_json_file_path):
        try:
            with open(config_json_file_path, encoding='utf-8-sig') as config_json_file_object:
                try:
                    return json.load(config_json_file_object)
                except JSONDecodeError:
                    print("The given file '" + config_json_file_path + "' is not a path to a valid JSON file.");
                    return {}
        except IOError:
            print("The given file '" + config_json_file_path + "' cannot be found.")
            return {}

