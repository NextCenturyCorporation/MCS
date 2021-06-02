
import atexit
import glob
import json
import logging
import os
import random
from typing import Dict, List

import ai2thor.controller
import ai2thor.server
import marshmallow
import numpy as np
import PIL

logger = logging.getLogger(__name__)


# How far the player can reach.  I think this value needs to be bigger
# than the MAX_MOVE_DISTANCE or else the player may not be able to move
# into a position to reach some objects (it may be mathematically impossible).
# TODO Reduce this number once the player can crouch down to reach and
# pickup small objects on the floor.

DEFAULT_MOVE = 0.1

from .action import Action
from .config_manager import (ConfigManager, SceneConfiguration,
                             SceneConfigurationSchema)
from .controller_events import (ControllerEventPayload, EventType,
                                PredictionPayload)
from .controller_output_handler import ControllerOutputHandler
from .goal_metadata import GoalMetadata
from .step_metadata import StepMetadata
from .uploader import S3Uploader
from .validation import Validation


def __reset_override(self, scene):
    # From https://github.com/allenai/ai2thor/blob/2.5.0/ai2thor/controller.py#L503-L525 # noqa: E501
    # Remove the error check: if scene not in self.scenes_in_build
    self.server.send(dict(action='Reset', sceneName=scene, sequenceId=0))
    self.last_event = self.server.receive()
    self.last_event = self.step(
        action='Initialize',
        **self.initialization_parameters
    )
    return self.last_event


ai2thor.controller.Controller.reset = __reset_override


def __image_depth_override(self, image_depth_data, **kwargs):
    # From https://github.com/NextCenturyCorporation/ai2thor/blob/47a9d0802861ba8d7a2a7a6d943a46db28ddbaab/ai2thor/server.py#L232-L240 # noqa: E501
    # The MCS depth shader in Unity is completely different now, so override
    # the original AI2-THOR depth image code. Just return what Unity sends us.
    image_depth = ai2thor.server.read_buffer_image(
        image_depth_data,
        self.screen_width,
        self.screen_height
    )
    return image_depth


ai2thor.server.Event._image_depth = __image_depth_override


class NumpyAwareEncoderOverride(json.JSONEncoder):
    # From https://github.com/allenai/ai2thor/blob/bd35d2cb887faee8b87aa04bd9373b027eb39f17/ai2thor/server.py#L17-L24 # noqa: E501
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.generic):
            return np.asscalar(obj)
        return super(NumpyAwareEncoderOverride, self).default(obj)


ai2thor.server.NumpyAwareEncoder = NumpyAwareEncoderOverride


class Controller():
    """
    MCS Controller class implementation for the MCS wrapper of the AI2-THOR
    library.

    https://ai2thor.allenai.org/ithor/documentation/

    Parameters
    ----------
    config_file_path: str, optional
        Path to configuration file to read in and set various properties,
        such as metadata level and whether or not to save history files
        (default None)
    """

    # AI2-THOR creates a square grid across the scene that is
    # uses for "snap-to-grid" movement. (This value may not
    # really matter because we set continuous to True in
    # the step input.)
    GRID_SIZE = 0.1

    MAX_FORCE = 50.0

    DEFAULT_HORIZON = 0
    DEFAULT_ROTATION = 0
    DEFAULT_FORCE = 0.5
    DEFAULT_AMOUNT = 0.5
    DEFAULT_IMG_COORD = 0
    DEFAULT_OBJECT_MOVE_AMOUNT = 1

    MAX_FORCE = 1
    MIN_FORCE = 0
    MAX_AMOUNT = 1
    MIN_AMOUNT = 0

    ROTATION_KEY = 'rotation'
    HORIZON_KEY = 'horizon'
    FORCE_KEY = 'force'
    AMOUNT_KEY = 'amount'

    OBJECT_IMAGE_COORDS_X_KEY = 'objectImageCoordsX'
    OBJECT_IMAGE_COORDS_Y_KEY = 'objectImageCoordsY'
    RECEPTACLE_IMAGE_COORDS_X_KEY = 'receptacleObjectImageCoordsX'
    RECEPTACLE_IMAGE_COORDS_Y_KEY = 'receptacleObjectImageCoordsY'

    # used for EndHabituation teleport
    TELEPORT_X_POS = 'xPosition'
    TELEPORT_Z_POS = 'zPosition'
    TELEPORT_Y_ROT = 'yRotation'

    # Hard coding actions that effect MoveMagnitude so the appropriate
    # value is set based off of the action
    # TODO: Move this to an enum or some place, so that you can determine
    # special move interactions that way
    FORCE_ACTIONS = ["ThrowObject", "PushObject", "PullObject"]
    OBJECT_MOVE_ACTIONS = ["CloseObject", "OpenObject"]
    MOVE_ACTIONS = ["MoveAhead", "MoveLeft", "MoveRight", "MoveBack"]

    AWS_CREDENTIALS_FOLDER = os.path.expanduser('~') + '/.aws/'
    AWS_CREDENTIALS_FILE = os.path.expanduser('~') + '/.aws/credentials'

    AWS_ACCESS_KEY_ID = 'aws_access_key_id'
    AWS_SECRET_ACCESS_KEY = 'aws_secret_access_key'

    def __init__(self, unity_app_file_path, config):

        self._subscribers = []

        self._end_scene_not_registered = True

        self._config = config

        self._output_handler = ControllerOutputHandler(self._config)

        self._controller = ai2thor.controller.Controller(
            quality='Medium',
            fullscreen=False,
            # The headless flag does not work for me
            headless=False,
            local_executable_path=unity_app_file_path,
            width=self._config.get_screen_width(),
            height=self._config.get_screen_height(),
            # Set the name of our Scene in our Unity app
            scene='MCS',
            logs=True,
            # This constructor always initializes a scene, so add a scene
            # config to ensure it doesn't error
            sceneConfig={
                "objects": []
            }
        )

        self._on_init()

    def subscribe(self, subscriber):
        if subscriber not in self._subscribers:
            self._subscribers.append(subscriber)

    def _publish_event(self, event_type: EventType,
                       payload: ControllerEventPayload):
        for subscriber in self._subscribers:
            # TODO should we make a deep copy of the payload so subscribers
            # cannot change source data?
            # seems like performance vs safety

            # TODO passing the whole controller is clearly a bad idea
            # change later
            subscriber.on_event(event_type, payload)

    # TODO this is a huge data dumpster and needs to be thought about

    def _create_event_payload(self):
        payload = ControllerEventPayload(
            self.__output_folder,
            self._config,
            self.__step_number,
            self._scene_config,
            self.__habituation_trial,
            self._goal)
        return payload

    # Pixel coordinates are expected to start at the top left, but
    # in Unity, (0,0) is the bottom left.

    def _convert_y_image_coord_for_unity(self, y_coord):
        if(y_coord != 0):
            return self._config.get_screen_height() - y_coord
        else:
            return y_coord

    def _on_init(self):

        self.__noise_enabled = self._config.is_noise_enabled()
        self.__seed = self._config.get_seed()

        if self.__seed:
            random.seed(self.__seed)

        self._goal = GoalMetadata()
        self.__habituation_trial = 1
        # Output folder used to save debug image, video, and JSON files.
        self.__output_folder = None
        self._scene_config = None
        self.__step_number = 0

        # Whether or not to show depth maps or object masks is based on
        # metadata tier (the default for these if no metadata level is
        # set or metadata is set to `none`, is `False`)

        if ((self._config.get_aws_access_key_id() is not None) and
                (self._config.get_aws_secret_access_key() is not None)):
            if not os.path.exists(self.AWS_CREDENTIALS_FOLDER):
                os.makedirs(self.AWS_CREDENTIALS_FOLDER)
            # From https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html # noqa: E501
            with open(self.AWS_CREDENTIALS_FILE, 'w') as credentials_file:
                credentials_file.write(
                    '[default]\n' +
                    self.AWS_ACCESS_KEY_ID +
                    ' = ' +
                    self._config.get_aws_access_key_id() +
                    '\n' +
                    self.AWS_SECRET_ACCESS_KEY +
                    ' = ' +
                    self._config.get_aws_secret_access_key() +
                    '\n'
                )

    def end_scene(self, choice, confidence=1.0):
        """
        Ends the current scene.  Calling end_scene() before calling
        start_scene() will do nothing.

        Parameters
        ----------
        choice : string, optional
            The selected choice required for ending scenes with
            violation-of-expectation or classification goals.
            Is not required for other goals. (default None)
        confidence : float, optional
            The choice confidence between 0 and 1 required for ending scenes
            with violation-of-expectation or classification goals.
            Is not required for other goals. (default None)

            Note: when an issue causes the program to exit prematurely or
            end_scene isn't properly called but history_enabled is true,
            this value will be written to file as -1.
        """
        uploader = None
        if self._config.is_evaluation():
            uploader = S3Uploader(
                s3_bucket=self._config.get_s3_bucket()
            )

        # TODO uploader be passed to classes that need
        # it on early on via dependency injection?
        payload = self._create_event_payload()
        payload.choice = choice
        payload.confidence = confidence
        payload.uploader = uploader
        payload.uploader_folder_prefix = self._config.get_s3_folder()
        self._publish_event(EventType.ON_END_SCENE, payload)

        if (not self._end_scene_not_registered):
            atexit.unregister(self.end_scene)
            self._end_scene_not_registered = True

    def _convert_scene_config(self, config_data) -> SceneConfiguration:
        if isinstance(config_data, SceneConfiguration):
            scene_config = config_data
        else:
            schema = SceneConfigurationSchema()
            scene_config = schema.load(config_data)
        return scene_config

    def start_scene(self, config_data):
        """
        Starts a new scene using the given scene configuration data dict and
        returns the scene output data object.

        Parameters
        ----------
        config_data : SceneConfiguration or dict that can be serialized to
            SceneConfiguration
            The MCS scene configuration data for the scene to start.

        Returns
        -------
        StepMetadata
            The output data object from the start of the scene (the output from
            an "Initialize" action).
        """

        scene_config = self._convert_scene_config(config_data)

        self._scene_config = scene_config
        self.__habituation_trial = 1
        self.__step_number = 0
        self._goal = self._scene_config.retrieve_goal()

        skip_preview_phase = (scene_config.goal is not None and
                              scene_config.goal.skip_preview_phase)

        if (self.isFileWritingEnabled()):
            os.makedirs('./' + scene_config.name, exist_ok=True)
            self.__output_folder = './' + scene_config.name + '/'
            file_list = glob.glob(self.__output_folder + '*')
            for file_path in file_list:
                os.remove(file_path)

        sc = SceneConfigurationSchema(
            unknown=marshmallow.EXCLUDE).dump(
            scene_config)
        sc = self._remove_none(sc)
        wrapped_step = self.wrap_step(
            action='Initialize',
            sceneConfig=sc
        )
        step_output = self._controller.step(wrapped_step)

        self._output_handler.set_scene_config(scene_config)
        (pre_restrict_output, output) = self._output_handler.handle_output(
            step_output, self._goal, self.__step_number,
            self.__habituation_trial)

        if not skip_preview_phase:
            if (self._goal is not None and
                    self._goal.last_preview_phase_step > 0):
                image_list = output.image_list
                depth_map_list = output.depth_map_list
                object_mask_list = output.object_mask_list

                logger.debug('STARTING PREVIEW PHASE...')

                for i in range(0, self._goal.last_preview_phase_step):
                    output = self.step('Pass')
                    image_list = image_list + output.image_list
                    depth_map_list = depth_map_list + output.depth_map_list
                    object_mask_list = (object_mask_list +
                                        output.object_mask_list)

                logger.debug('ENDING PREVIEW PHASE')

                output.image_list = image_list
                output.depth_map_list = depth_map_list
                output.object_mask_list = object_mask_list

            logger.debug('NO PREVIEW PHASE')

            # TODO Should this be in the if block?  Now that we are using
            # subscribers, we may want to always register
            if(self._end_scene_not_registered is True and
                    (self._config.is_history_enabled() or
                     self._config.is_evaluation())):
                # make sure history file is written when program exits
                atexit.register(self.end_scene, choice="", confidence=-1)
                self._end_scene_not_registered = False

        payload = self._create_event_payload()
        payload.wrapped_step = wrapped_step
        payload.step_metadata = step_output
        payload.step_output = pre_restrict_output
        payload.restricted_step_output = output
        self._publish_event(
            EventType.ON_START_SCENE, payload)

        return output

    def isFileWritingEnabled(self):
        return self._scene_config.name is not None and (
            self._config.is_evaluation() or
            self._config.is_save_debug_images() or
            self._config.is_save_debug_json() or
            self._config.is_video_enabled()
        )

    # TODO: may need to reevaluate validation strategy/error handling in the
    # future
    """
    Need a validation/conversion step for what ai2thor will accept as input
    to keep parameters more simple for the user (in this case, wrapping
    rotation degrees into an object)
    """

    def validate_and_convert_params(self, action, **kwargs):
        moveMagnitude = DEFAULT_MOVE
        rotation = kwargs.get(self.ROTATION_KEY, self.DEFAULT_ROTATION)
        horizon = kwargs.get(self.HORIZON_KEY, self.DEFAULT_HORIZON)
        amount = kwargs.get(
            self.AMOUNT_KEY,
            self.DEFAULT_OBJECT_MOVE_AMOUNT
            if action in self.OBJECT_MOVE_ACTIONS
            else self.DEFAULT_AMOUNT
        )
        force = kwargs.get(self.FORCE_KEY, self.DEFAULT_FORCE)

        objectImageCoordsX = kwargs.get(
            self.OBJECT_IMAGE_COORDS_X_KEY, self.DEFAULT_IMG_COORD)
        objectImageCoordsY = kwargs.get(
            self.OBJECT_IMAGE_COORDS_Y_KEY, self.DEFAULT_IMG_COORD)
        receptacleObjectImageCoordsX = kwargs.get(
            self.RECEPTACLE_IMAGE_COORDS_X_KEY, self.DEFAULT_IMG_COORD)
        receptacleObjectImageCoordsY = kwargs.get(
            self.RECEPTACLE_IMAGE_COORDS_Y_KEY, self.DEFAULT_IMG_COORD)

        if not Validation.is_number(amount, self.AMOUNT_KEY):
            # The default for open/close is 1, the default for "Move" actions
            # is 0.5
            if action in self.OBJECT_MOVE_ACTIONS:
                amount = self.DEFAULT_OBJECT_MOVE_AMOUNT
            else:
                amount = self.DEFAULT_AMOUNT

        if not Validation.is_number(force, self.FORCE_KEY):
            force = self.DEFAULT_FORCE

        # Check object directions are numbers
        if not Validation.is_number(
                objectImageCoordsX,
                self.OBJECT_IMAGE_COORDS_X_KEY):
            objectImageCoordsX = self.DEFAULT_IMG_COORD

        if not Validation.is_number(
                objectImageCoordsY,
                self.OBJECT_IMAGE_COORDS_Y_KEY):
            objectImageCoordsY = self.DEFAULT_IMG_COORD

        # Check receptacle directions are numbers
        if not Validation.is_number(
                receptacleObjectImageCoordsX,
                self.RECEPTACLE_IMAGE_COORDS_X_KEY):
            receptacleObjectImageCoordsX = self.DEFAULT_IMG_COORD

        if not Validation.is_number(
                receptacleObjectImageCoordsY,
                self.RECEPTACLE_IMAGE_COORDS_Y_KEY):
            receptacleObjectImageCoordsY = self.DEFAULT_IMG_COORD

        amount = Validation.is_in_range(
            amount,
            self.MIN_AMOUNT,
            self.MAX_AMOUNT,
            self.DEFAULT_AMOUNT,
            self.AMOUNT_KEY)
        force = Validation.is_in_range(
            force,
            self.MIN_FORCE,
            self.MAX_FORCE,
            self.DEFAULT_FORCE,
            self.FORCE_KEY)

        # TODO Consider the current "head tilt" value while validating the
        # input "horizon" value.

        # Set the Move Magnitude to the appropriate amount based on the action
        if action in self.FORCE_ACTIONS:
            moveMagnitude = force * self.MAX_FORCE

        if action in self.OBJECT_MOVE_ACTIONS:
            moveMagnitude = amount

        if action in self.MOVE_ACTIONS:
            moveMagnitude = DEFAULT_MOVE

        # Add in noise if noise is enable
        if self.__noise_enabled:
            rotation = rotation * (1 + self.generate_noise())
            horizon = horizon * (1 + self.generate_noise())
            moveMagnitude = moveMagnitude * (1 + self.generate_noise())

        rotation_vector = {}
        rotation_vector['y'] = rotation

        object_vector = {}
        object_vector['x'] = float(objectImageCoordsX)
        object_vector['y'] = self._convert_y_image_coord_for_unity(
            float(objectImageCoordsY))

        receptacle_vector = {}
        receptacle_vector['x'] = float(receptacleObjectImageCoordsX)
        receptacle_vector['y'] = self._convert_y_image_coord_for_unity(
            float(receptacleObjectImageCoordsY))

        teleportRotInput = kwargs.get(self.TELEPORT_Y_ROT)
        teleportPosXInput = kwargs.get(self.TELEPORT_X_POS)
        teleportPosZInput = kwargs.get(self.TELEPORT_Z_POS)

        teleportRotation = None
        teleportPosition = None

        if teleportRotInput is not None and Validation.is_number(
                teleportRotInput):
            teleportRotation = {}
            teleportRotation['y'] = kwargs.get(self.TELEPORT_Y_ROT)

        if (teleportPosXInput is not None and
                Validation.is_number(teleportPosXInput) and
                teleportPosZInput is not None and
                Validation.is_number(teleportPosZInput)):
            teleportPosition = {}
            teleportPosition['x'] = teleportPosXInput
            teleportPosition['z'] = teleportPosZInput

        return dict(
            objectId=kwargs.get("objectId", None),
            receptacleObjectId=kwargs.get("receptacleObjectId", None),
            rotation=rotation_vector,
            horizon=horizon,
            teleportRotation=teleportRotation,
            teleportPosition=teleportPosition,
            moveMagnitude=moveMagnitude,
            objectImageCoords=object_vector,
            receptacleObjectImageCoords=receptacle_vector
        )

    # Override
    def step(self, action: str, **kwargs) -> StepMetadata:
        """
        Runs the given action within the current scene.

        Parameters
        ----------
        action : string
            A selected action string from the list of available actions.
        **kwargs
            Zero or more key-and-value parameters for the action.

        Returns
        -------
        StepMetadata
            The MCS output data object from after the selected action and the
            physics simulation were run. Returns None if you have passed the
            "last_step" of this scene.
        """
        if (self._goal.last_step is not None and
                self._goal.last_step == self.__step_number):
            logger.warning(
                "You have passed the last step for this scene. "
                "Ignoring your action. Please call controller.end_scene() "
                "now.")
            return None

        if ',' in action:
            action, kwargs = Action.input_to_action_and_params(action)

        action_list = self._goal.retrieve_action_list_at_step(
            self.__step_number)
        # Only continue with this action step if the given action and
        # parameters are in the restricted action list.
        continue_with_step = False
        for restricted_action, restricted_params in action_list:
            if action == restricted_action:
                # If this action doesn't have restricted parameters, or each
                # input parameter is in the restricted parameters, it's OK.
                if len(restricted_params.items()) == 0 or all([
                    restricted_params.get(key) == value
                    for key, value in kwargs.items()
                ]):
                    continue_with_step = True
                    break
        if not continue_with_step:
            logger.warning(
                f"The given action '{action}' with parameters "
                f"'{kwargs}' isn't in the action_list. Ignoring your action. "
                f"Please call controller.step() with an action in the "
                f"action_list. Possible actions at step {self.__step_number}:"
            )
            for action_data in action_list:
                logger.warning(f'    {action_data}')
            return None

        self.__step_number += 1

        payload = self._create_event_payload()
        payload.action = action
        payload.action_args = kwargs
        self._publish_event(
            EventType.ON_BEFORE_STEP,
            payload)

        params = self.validate_and_convert_params(action, **kwargs)

        # Only call mcs_action_to_ai2thor_action AFTER calling
        # validate_and_convert_params
        action = self.mcs_action_to_ai2thor_action(action)

        if (action == 'EndHabituation'):
            self.__habituation_trial += 1

        if (self._goal.last_step is not None and
                self._goal.last_step == self.__step_number):
            logger.warning(
                "This is your last step for this scene. All "
                "your future actions will be skipped. Please call "
                "controller.end_scene() now.")

        step_action = self.wrap_step(action=action, **params)
        step_output = self._controller.step(step_action)

        (pre_restrict_output, output) = self._output_handler.handle_output(
            step_output, self._goal, self.__step_number,
            self.__habituation_trial)

        payload = self._create_event_payload()
        # do we need both outputs?
        payload.ai2thor_action = action
        payload.step_params = params
        payload.kwargs = kwargs
        payload.wrapped_step = step_action
        payload.step_metadata = step_output
        payload.step_output = pre_restrict_output
        payload.restricted_step_output = output
        self._publish_event(
            EventType.ON_AFTER_STEP,
            payload)

        return output

    def make_step_prediction(self, choice: str = None,
                             confidence: float = None,
                             violations_xy_list: List[Dict[str, float]] = None,
                             heatmap_img: PIL.Image.Image = None,
                             internal_state: object = None,) -> None:
        """Make a prediction on the previously taken step/action.

        Parameters
        ----------
        choice : string, optional
            The selected choice for per frame prediction with
            violation-of-expectation or classification goals.
            Is not required for other goals. (default None)
        confidence : float, optional
            The choice confidence between 0 and 1 required by the end of
            scenes with violation-of-expectation or classification goals.
            Is not required for other goals. (default None)
        violations_xy_list : List[Dict[str, float]], optional
            A list of one or more (x, y) locations (ex: [{"x": 1, "y": 3.4}]),
            each representing a potential violation-of-expectation. Required
            on each step for passive tasks. (default None)
        heatmap_img : PIL.Image.Image, optional
            An image representing scene plausiblility at a particular
            moment. During evaluation, this image will be recorded as a frame
            of a heatmap video for review but is ignored otherwise.
            (default None)
        internal_state : object, optional
            A properly formatted json object representing various kinds of
            internal states at a particular moment. Examples include the
            estimated position of the agent, current map of the world, etc.
            (default None)

        Returns
        -------
            None
        """

        payload = PredictionPayload(
            self._config,
            choice,
            confidence,
            violations_xy_list,
            heatmap_img,
            internal_state)
        self._publish_event(EventType.ON_PREDICTION, payload)

    def mcs_action_to_ai2thor_action(self, action):
        if action == Action.CLOSE_OBJECT.value:
            # The AI2-THOR Python library has buggy error checking
            # specifically for the CloseObject action,
            # so just use our own custom action here.
            return "MCSCloseObject"

        if action == Action.DROP_OBJECT.value:
            return "DropHandObject"

        if action == Action.OPEN_OBJECT.value:
            # The AI2-THOR Python library has buggy error checking
            # specifically for the OpenObject action,
            # so just use our own custom action here.
            return "MCSOpenObject"

        # if action == Action.ROTATE_OBJECT_IN_HAND.value:
        #     return "RotateHand"

        return action

    def retrieve_action_list_at_step(self, goal, step_number):
        return goal.retrieve_action_list_at_step(step_number)

    def retrieve_object_states(self, object_id):
        """Return the state list at the current step for the object with the
        given ID from the scene configuration data, if any."""
        self._scene_config.retrieve_object_states(
            object_id,
            self.__step_number)

    def stop_simulation(self):
        """Stop the 3D simulation environment. This controller won't work any
        more."""
        self._controller.stop()

    def _remove_none(self, d):
        '''Remove all none's from dictionaries'''
        for key, value in dict(d).items():
            if isinstance(value, dict):
                d[key] = self._remove_none(value)
            if isinstance(value, list):
                for index, val in enumerate(value):
                    if isinstance(val, dict):
                        value[index] = self._remove_none(val)
            if value is None:
                del d[key]
        return d

    def wrap_step(self, **kwargs):
        # whether or not to randomize segmentation mask colors
        consistentColors = False
        metadata_tier = self._config.get_metadata_tier()
        if(metadata_tier == ConfigManager.CONFIG_METADATA_TIER_ORACLE):
            consistentColors = True

        # Create the step data dict for the AI2-THOR step function.
        step_data = dict(
            continuous=True,
            gridSize=self.GRID_SIZE,
            logs=True,
            renderDepthImage=self._config.is_depth_maps_enabled(),
            renderObjectImage=self._config.is_object_masks_enabled(),
            snapToGrid=False,
            consistentColors=consistentColors,
            **kwargs
        )

        return step_data

    def generate_noise(self):
        """
        Returns a random value between -0.05 and 0.05 used to add noise to all
        numerical action parameters noise_enabled is True.
        Returns
        -------
        float
            A value between -0.05 and 0.05 (using random.uniform).
        """

        return random.uniform(-0.5, 0.5)

    def get_metadata_level(self):
        """
        Returns the current metadata level set in the config. If none
        specified, returns 'default'.

        Returns
        -------
        string
            A string containing the current metadata level.
        """
        return self._config.get_metadata_tier()
