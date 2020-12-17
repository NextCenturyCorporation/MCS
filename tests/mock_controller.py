import ai2thor.server
import numpy
import os

from machine_common_sense.controller import Controller
from machine_common_sense.pose import Pose
from machine_common_sense.action import Action
from machine_common_sense.config_manager import ConfigManager

MOCK_VARIABLES = {
    'event_count': 5,
    'frame': numpy.array([[0]], dtype=numpy.uint8),
    'depth_frame': numpy.array([[[0, 0, 0]]], dtype=numpy.uint8),
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

        # Need to clear any previously set environment variables
        # so that they don't affect test cases
        check_config_path = os.getenv(
            ConfigManager.CONFIG_FILE_ENV_VAR, None)

        if(check_config_path is not None):
            os.environ.pop(ConfigManager.CONFIG_FILE_ENV_VAR)

        check_metadata_tier = os.getenv(
            ConfigManager.METADATA_ENV_VAR, None)

        if(check_metadata_tier is not None):
            os.environ.pop(ConfigManager.METADATA_ENV_VAR)

        check_debug_mode = os.getenv('MCS_DEBUG_MODE', None)

        if(check_debug_mode is not None):
            os.environ.pop('MCS_DEBUG_MODE')

        self._controller = MockController()
        self._config = ConfigManager()
        self._update_screen_size()
        self._on_init()

    def get_last_step_data(self):
        return self._controller.get_last_step_data()

    def render_mask_images(self):
        self._update_internal_config(depth_maps=True, object_masks=True)

    def set_goal(self, goal):
        self._goal = goal

    def set_metadata_tier(self, mode):
        self._metadata_tier = mode
