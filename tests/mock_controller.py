import os

import ai2thor.server
import numpy

from machine_common_sense.action import Action
from machine_common_sense.config_manager import ConfigManager
from machine_common_sense.controller import Controller
from machine_common_sense.controller_output_handler import \
    ControllerOutputHandler
from machine_common_sense.pose import Pose

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
        self._subscribers = []

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
        return ai2thor.server.MultiAgentEvent(
            0, [event for _ in range(MOCK_VARIABLES['event_count'])]
        )

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

    def subscribe(self, subscriber):
        if subscriber not in self._subscribers:
            self._subscribers.append(subscriber)


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

        self._subscribers = []

        self._end_scene_not_registered = False  # atexit not needed for tests
        self._controller = MockController()
        self._config = ConfigManager(config_file_or_dict={})
        self._config._config[
            ConfigManager.CONFIG_DEFAULT_SECTION
        ] = {}
        self._output_handler = ControllerOutputHandler(self._config)
        self._on_init()
        self._set_config(self._config)

    def get_last_step_data(self):
        return self._controller.get_last_step_data()

    def set_goal(self, goal):
        self._goal = goal

    def set_metadata_tier(self, mode):
        if not self._config:
            self._config = ConfigManager()
        self._config.set_metadata_tier(mode)
