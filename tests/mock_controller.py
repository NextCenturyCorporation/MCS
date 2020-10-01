import ai2thor.server
import numpy

from machine_common_sense.controller import Controller
from machine_common_sense.pose import Pose
from machine_common_sense.action import Action

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
        'pose': Pose.STANDING.name,
        'lastActionStatus': 'SUCCESSFUL',
        'objects': [],
        'screenHeight': 400,
        'screenWidth': 600,
        'structuralObjects': []
    }
}


class MockController():
    '''Mock of the Controller class from the AI2-THOR library.'''

    def __init__(self):
        self.__last_step_data = None
        self.__last_metadata = MOCK_VARIABLES['metadata'].copy()

    def step(self, data):
        self.__last_step_data = data
        self.update_metadata(data)
        metadata = self.__last_metadata

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

    def update_metadata(self, data: dict) -> dict:

        if data['action'] == Action.CRAWL.value:
            self.__last_metadata['pose'] = Pose.CRAWLING.name
        elif (data['action'] == Action.STAND.value and
              self.__last_metadata['pose'] != Pose.LYING.name):
            self.__last_metadata['pose'] = Pose.STANDING.name
        elif data['action'] == Action.LIE_DOWN.value:
            self.__last_metadata['pose'] = Pose.LYING.name


class MockControllerAI2THOR(Controller):
    '''Mock of the ControllerAI2THOR class from the MCS library.'''

    def __init__(self):
        # Do NOT call superclass __init__ function
        self._controller = MockController()
        self._update_screen_size()
        self._on_init()

    def get_last_step_data(self):
        return self._controller.get_last_step_data()

    def render_mask_images(self):
        self._update_internal_config(depth_masks=True, object_masks=True)

    def set_config(self, config):
        self._config = config

    def set_goal(self, goal):
        self._goal = goal
