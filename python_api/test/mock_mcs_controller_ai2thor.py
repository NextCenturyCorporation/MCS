import ai2thor.server
import numpy

from machine_common_sense.mcs_controller_ai2thor import MCS_Controller_AI2THOR

MOCK_VARIABLES = {
    'event_count': 5,
    'frame': numpy.array([[0]], dtype=numpy.uint8),
    'depth_frame': numpy.array([[0]], dtype=numpy.uint8),
    'instance_segmentation_frame': numpy.array([[0]], dtype=numpy.uint8),
    'metadata': {
        'agent': {
            'cameraHorizon': 0.0,
            'position': {
                'x': 0.0,
                'y': 0.0,
                'z': 0.0
            },
            'rotation': {
                'y': 0.0
            }
        },
        'lastActionStatus': 'SUCCESSFUL',
        'objects': [],
        'screenHeight': 400,
        'screenWidth': 600,
        'structuralObjects': []
    }
}


class Mock_AI2THOR_Controller():
    def __init__(self):
        self.__last_step_data = None
        pass

    def step(self, data):
        self.__last_step_data = data
        metadata = MOCK_VARIABLES['metadata'].copy()
        event = ai2thor.server.Event(metadata)
        event.frame = MOCK_VARIABLES['frame'].copy()
        event.depth_frame = MOCK_VARIABLES['depth_frame'].copy()
        event.instance_segmentation_frame = MOCK_VARIABLES[
            'instance_segmentation_frame'
        ].copy()
        output = ai2thor.server.MultiAgentEvent(
            0, [event for _ in range(0, MOCK_VARIABLES['event_count'])])
        return output

    def get_last_step_data(self):
        return self.__last_step_data


class Mock_MCS_Controller_AI2THOR(MCS_Controller_AI2THOR):

    def __init__(self):
        # Do NOT call superclass __init__ function
        self._controller = Mock_AI2THOR_Controller()
        self.on_init()

    def get_last_step_data(self):
        return self._controller.get_last_step_data()

    def set_config(self, config):
        self._config = config

    def set_goal(self, goal):
        self._goal = goal
