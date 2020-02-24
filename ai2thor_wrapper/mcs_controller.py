from mcs_step_output import MCS_Step_Output

class MCS_Controller:

    def __init__(self):
        # TODO Override
        pass

    def end_scene(self, classification, confidence):
        # TODO Override
        pass

    def start_scene(self, config_data):
        # TODO Override
        return MCS_Step_Output()

    def step(self, action, **kwargs):
        # TODO Override
        return MCS_Step_Output()

