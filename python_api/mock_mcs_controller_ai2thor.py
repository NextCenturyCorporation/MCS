from mcs_controller_ai2thor import MCS_Controller_AI2THOR
from mcs_step_output import MCS_Step_Output

class Mock_AI2THOR_Controller():
    def __init__(self):
        pass

    def step(self, data):
        # TODO MCS-15 Return an AI2-THOR step Metadata object: https://ai2thor.allenai.org/ithor/documentation/metadata/
        return {}

class Mock_MCS_Controller_AI2THOR(MCS_Controller_AI2THOR):

    def __init__(self):
        # Do NOT call superclass __init__ function
        self.__controller = Mock_AI2THOR_Controller()
        self.on_init()

