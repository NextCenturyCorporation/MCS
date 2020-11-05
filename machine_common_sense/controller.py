import copy
import datetime
import glob
import json
import numpy as np
import os
import random
import pathlib
import yaml
import PIL
import ast
from typing import Dict, List

import ai2thor.controller
import ai2thor.server

# How far the player can reach.  I think this value needs to be bigger
# than the MAX_MOVE_DISTANCE or else the player may not be able to move
# into a position to reach some objects (it may be mathematically impossible).
# TODO Reduce this number once the player can crouch down to reach and
# pickup small objects on the floor.
MAX_REACH_DISTANCE = 1.0

# How far the player can move with a single step.
MOVE_DISTANCE = 0.1

# Performer camera 'y' position
PERFORMER_CAMERA_Y = 0.4625

from .action import Action
from .goal_metadata import GoalMetadata
from .object_metadata import ObjectMetadata
from .plotter import TopDownPlotter
from .pose import Pose
from .return_status import ReturnStatus
from .reward import Reward
from .scene_history import SceneHistory
from .step_metadata import StepMetadata
from .recorder import VideoRecorder
from .uploader import S3Uploader
from .util import Util
from .history_writer import HistoryWriter

# From https://github.com/NextCenturyCorporation/ai2thor/blob/master/ai2thor/server.py#L232-L240 # noqa: E501


def __image_depth_override(self, image_depth_data, **kwargs):
    # The MCS depth shader in Unity is completely different now, so override
    # the original AI2-THOR depth image code.
    # Just return what Unity sends us.
    image_depth = ai2thor.server.read_buffer_image(
        image_depth_data, self.screen_width, self.screen_height, **kwargs)
    return image_depth


ai2thor.server.Event._image_depth = __image_depth_override


class Controller():
    """
    MCS Controller class implementation for the MCS wrapper of the AI2-THOR
    library.

    https://ai2thor.allenai.org/ithor/documentation/

    Parameters
    ----------
    debug : boolean, optional
        Whether to save MCS output debug files in this folder.
        (default False)
    enable_noise : boolean, optional
        Whether to add random noise to the numerical amounts in movement
        and object interaction action parameters.
        (default False)
    seed : int, optional
        A seed for the Python random number generator.
        (default None)
    history_enabled: boolean, optional
        Whether to save all the history files and generated image
        history to local disk or not.
        (default False)
    """

    ACTION_LIST = [item.value for item in Action]

    # Please keep the aspect ratio as 3:2 because the IntPhys scenes are built
    # on this assumption.
    SCREEN_WIDTH_DEFAULT = 600
    SCREEN_WIDTH_MIN = 450

    # AI2-THOR creates a square grid across the scene that is
    # uses for "snap-to-grid" movement. (This value may not
    # really matter because we set continuous to True in
    # the step input.)
    GRID_SIZE = 0.1
    # Is there any way to get FPS from ai2thor?
    # 20 FPS relies on the assumption that Time.deltaTime is 0.05 in Unity
    FPS_FRAME_RATE = 20

    DEFAULT_CLIPPING_PLANE_FAR = 15.0

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

    PLACEHOLDER = 'placeholder'
    VISUAL = 'visual'
    DEPTH = 'depth'
    SEGMENTATION = 'segmentation'
    HEATMAP = 'heatmap'
    TOPDOWN = 'topdown'

    OBJECT_IMAGE_COORDS_X_KEY = 'objectImageCoordsX'
    OBJECT_IMAGE_COORDS_Y_KEY = 'objectImageCoordsY'
    RECEPTACLE_IMAGE_COORDS_X_KEY = 'receptacleObjectImageCoordsX'
    RECEPTACLE_IMAGE_COORDS_Y_KEY = 'receptacleObjectImageCoordsY'

    # Hard coding actions that effect MoveMagnitude so the appropriate
    # value is set based off of the action
    # TODO: Move this to an enum or some place, so that you can determine
    # special move interactions that way
    FORCE_ACTIONS = ["ThrowObject", "PushObject", "PullObject"]
    OBJECT_MOVE_ACTIONS = ["CloseObject", "OpenObject"]
    MOVE_ACTIONS = ["MoveAhead", "MoveLeft", "MoveRight", "MoveBack"]

    CONFIG_METADATA_TIER = 'metadata'
    # Normal metadata plus metadata for all hidden objects
    CONFIG_METADATA_TIER_ORACLE = 'oracle'
    # No metadata, except for the images, depth masks, object masks,
    # and haptic/audio feedback
    CONFIG_METADATA_TIER_LEVEL_2 = 'level2'
    # No metadata, except for the images, depth masks, and haptic/audio
    # feedback
    CONFIG_METADATA_TIER_LEVEL_1 = 'level1'

    CONFIG_EVALUATION = 'evaluation'

    AWS_CREDENTIALS_FOLDER = os.path.expanduser('~') + '/.aws/'
    AWS_CREDENTIALS_FILE = os.path.expanduser('~') + '/.aws/credentials'
    AWS_ACCESS_KEY_ID = 'aws_access_key_id'
    AWS_SECRET_ACCESS_KEY = 'aws_secret_access_key'

    CONFIG_AWS_ACCESS_KEY_ID = 'aws_access_key_id'
    CONFIG_AWS_SECRET_ACCESS_KEY = 'aws_secret_access_key'

    CONFIG_S3_BUCKET = 's3_bucket'
    CONFIG_S3_FOLDER = 's3_folder'
    CONFIG_TEAM = 'team'
    CONFIG_EVALUATION_NAME = 'evaluation_name'

    def __init__(self, unity_app_file_path, debug=False,
                 enable_noise=False, seed=None, size=None,
                 depth_maps=None, object_masks=None,
                 history_enabled=True):

        self._update_screen_size(size)

        self._controller = ai2thor.controller.Controller(
            quality='Medium',
            fullscreen=False,
            # The headless flag does not work for me
            headless=False,
            local_executable_path=unity_app_file_path,
            width=self.__screen_width,
            height=self.__screen_height,
            # Set the name of our Scene in our Unity app
            scene='MCS',
            logs=True,
            # This constructor always initializes a scene, so add a scene
            # config to ensure it doesn't error
            sceneConfig={
                "objects": []
            }
        )

        self._on_init(debug, enable_noise, seed, depth_maps,
                      object_masks, history_enabled)

    # Pixel coordinates are expected to start at the top left, but
    # in Unity, (0,0) is the bottom left.
    def _convert_y_image_coord_for_unity(self, y_coord):
        if(y_coord != 0):
            return self.__screen_height - y_coord
        else:
            return y_coord

    def _update_screen_size(self, size=None):
        self.__screen_width = self.SCREEN_WIDTH_DEFAULT
        self.__screen_height = int(self.SCREEN_WIDTH_DEFAULT / 3 * 2)
        if size and size >= self.SCREEN_WIDTH_MIN:
            self.__screen_width = size
            self.__screen_height = int(size / 3 * 2)

    def _update_internal_config(self, enable_noise=None, seed=None,
                                depth_maps=None, object_masks=None,
                                history_enabled=None):

        if enable_noise is not None:
            self.__enable_noise = enable_noise
        if seed is not None:
            self.__seed = seed
        if depth_maps is not None:
            self.__depth_maps = depth_maps
        if object_masks is not None:
            self.__object_masks = object_masks
        if history_enabled is not None:
            self.__history_enabled = history_enabled

    def _on_init(self, debug=False, enable_noise=False, seed=None,
                 depth_maps=None, object_masks=None,
                 history_enabled=True):

        self._config_file = os.getenv('MCS_CONFIG_FILE_PATH',
                                      './mcs_config.yaml')

        self.__debug_to_file = True if (
            debug is True or debug == 'file') else False
        self.__debug_to_terminal = True if (
            debug is True or debug == 'terminal') else False

        self.__enable_noise = enable_noise
        self.__seed = seed
        self.__history_enabled = history_enabled

        if self.__seed:
            random.seed(self.__seed)

        self._goal = GoalMetadata()
        self.__habituation_trial = 1
        self.__head_tilt = 0.0
        self.__output_folder = None  # Save output image files to debug
        self.__scene_configuration = None
        self.__step_number = 0
        self.__history_writer = None
        self.__history_item = None
        self.__uploader = None

        self._config = self.read_config_file()

        # Environment variable override for metadata property
        metadata_env_var = os.getenv('MCS_METADATA_LEVEL', None)

        if(metadata_env_var is None):
            self._metadata_tier = (
                self._config[self.CONFIG_METADATA_TIER]
                if self.CONFIG_METADATA_TIER in self._config
                else ''
            )
        else:
            self._metadata_tier = metadata_env_var

        # Order of preference for depth/object mask settings:
        # look for user specified depth_maps/object_masks properties,
        # then check config settings, else default to False
        if(self._metadata_tier == self.CONFIG_METADATA_TIER_LEVEL_1):
            self.__depth_maps = (
                depth_maps if depth_maps is not None else True)
            self.__object_masks = (
                object_masks if object_masks is not None else False)
        elif(self._metadata_tier == self.CONFIG_METADATA_TIER_LEVEL_2 or
             self._metadata_tier == self.CONFIG_METADATA_TIER_ORACLE):
            self.__depth_maps = (
                depth_maps if depth_maps is not None else True)
            self.__object_masks = (
                object_masks if object_masks is not None else True)
        else:
            self.__depth_maps = (
                depth_maps if depth_maps is not None else False)
            self.__object_masks = (
                object_masks if object_masks is not None else False)

        if ((self.CONFIG_AWS_ACCESS_KEY_ID in self._config) and
                (self.CONFIG_AWS_SECRET_ACCESS_KEY in self._config)):
            if not os.path.exists(self.AWS_CREDENTIALS_FOLDER):
                os.makedirs(self.AWS_CREDENTIALS_FOLDER)
            # From https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html # noqa: E501
            with open(self.AWS_CREDENTIALS_FILE, 'w') as credentials_file:
                credentials_file.write(
                    '[default]\n' +
                    self.AWS_ACCESS_KEY_ID +
                    ' = ' +
                    self._config[self.CONFIG_AWS_ACCESS_KEY_ID] +
                    '\n' +
                    self.AWS_SECRET_ACCESS_KEY +
                    ' = ' +
                    self._config[self.CONFIG_AWS_SECRET_ACCESS_KEY] +
                    '\n'
                )

    def _create_video_recorders(self):
        '''Create video recorders used to capture evaluation scenes for review
        '''
        output_folder = pathlib.Path(self.__output_folder)
        eval_name = self._config.get(self.CONFIG_EVALUATION_NAME, '')
        team = self._config.get(self.CONFIG_TEAM, '')
        scene_name = self.__scene_configuration.get(
            'name', '').replace('json', '')
        # strip prefix in scene_name
        if '/' in scene_name:
            scene_name = scene_name.rsplit('/', 1)[1]

        timestamp = self.generate_time()
        basename_template = ('_'.join(
            [eval_name, self._metadata_tier, team, scene_name,
             self.PLACEHOLDER, timestamp]) + '.mp4').replace(' ', '')

        visual_video_filename = basename_template.replace(
            self.PLACEHOLDER, self.VISUAL)
        self.__image_recorder = VideoRecorder(
            vid_path=output_folder / visual_video_filename,
            width=self.__screen_width,
            height=self.__screen_height,
            fps=self.FPS_FRAME_RATE)

        topdown_video_filename = basename_template.replace(
            self.PLACEHOLDER, self.TOPDOWN)
        self.__topdown_recorder = VideoRecorder(
            vid_path=output_folder / topdown_video_filename,
            width=self.__screen_width,
            height=self.__screen_height,
            fps=self.FPS_FRAME_RATE)

        heatmap_video_filename = basename_template.replace(
            self.PLACEHOLDER, self.HEATMAP)
        self.__heatmap_recorder = VideoRecorder(
            vid_path=output_folder / heatmap_video_filename,
            width=self.__screen_width,
            height=self.__screen_height,
            fps=self.FPS_FRAME_RATE)

        if self.__depth_maps:
            depth_video_filename = basename_template.replace(
                self.PLACEHOLDER, self.DEPTH)
            self.__depth_recorder = VideoRecorder(
                vid_path=output_folder / depth_video_filename,
                width=self.__screen_width,
                height=self.__screen_height,
                fps=self.FPS_FRAME_RATE)

        if self.__object_masks:
            segmentation_video_filename = basename_template.replace(
                self.PLACEHOLDER, self.SEGMENTATION)
            self.__segmentation_recorder = VideoRecorder(
                vid_path=output_folder / segmentation_video_filename,
                width=self.__screen_width,
                height=self.__screen_height,
                fps=self.FPS_FRAME_RATE)

    def get_seed_value(self):
        return self.__seed

    def end_scene(self, choice, confidence=1.0):
        """
        Ends the current scene.

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
        """
        if self.__history_enabled:
            self.__history_writer.add_step(self.__history_item)
            self.__history_writer.write_history_file(choice, confidence)

        if self._config.get(self.CONFIG_EVALUATION, False):
            self.__uploader = S3Uploader(
                s3_bucket=self._config.get(self.CONFIG_S3_BUCKET, None)
            )

            folder_prefix = self._config.get(self.CONFIG_S3_FOLDER, None)

            if self.__history_enabled:
                history_filename = pathlib.Path(
                    self.__history_writer.scene_history_file).name
                self.__uploader.upload_history(
                    history_path=self.__history_writer.scene_history_file,
                    s3_filename=(folder_prefix + '/' +
                                 self._config.get(
                                     self.CONFIG_EVALUATION_NAME, ''
                                 ) +
                                 '_' + self._metadata_tier +
                                 '_' + self._config.get(self.CONFIG_TEAM, '') +
                                 '_' + history_filename).replace(' ', '')
                )

            self.__topdown_recorder.finish()
            topdown_filename = self.__topdown_recorder.path.name
            self.__uploader.upload_video(
                video_path=self.__topdown_recorder.path,
                s3_filename=folder_prefix + '/' + topdown_filename
            )

            self.__image_recorder.finish()
            video_filename = self.__image_recorder.path.name
            self.__uploader.upload_video(
                video_path=self.__image_recorder.path,
                s3_filename=folder_prefix + '/' + video_filename
            )

            self.__heatmap_recorder.finish()
            video_filename = self.__heatmap_recorder.path.name
            self.__uploader.upload_video(
                video_path=self.__heatmap_recorder.path,
                s3_filename=folder_prefix + '/' + video_filename
            )

            if self.__depth_maps:
                self.__depth_recorder.finish()
                video_filename = self.__depth_recorder.path.name
                self.__uploader.upload_video(
                    video_path=self.__depth_recorder.path,
                    s3_filename=folder_prefix + '/' + video_filename
                )
            if self.__object_masks:
                self.__segmentation_recorder.finish()
                video_filename = self.__segmentation_recorder.path.name
                self.__uploader.upload_video(
                    video_path=self.__segmentation_recorder.path,
                    s3_filename=folder_prefix + '/' + video_filename
                )

    def start_scene(self, config_data):
        """
        Starts a new scene using the given scene configuration data dict and
        returns the scene output data object.

        Parameters
        ----------
        config_data : dict
            The MCS scene configuration data for the scene to start.

        Returns
        -------
        StepMetadata
            The output data object from the start of the scene (the output from
            an "Initialize" action).
        """

        self.__scene_configuration = config_data
        self.__habituation_trial = 1
        self.__step_number = 0
        self._goal = self.retrieve_goal(self.__scene_configuration)

        if self.__history_enabled:
            # Ensure the previous scene history writer has saved its file.
            if self.__history_writer:
                self.__history_writer.check_file_written()
            # Create a new scene history writer with each new scene (config
            # data) so we always create a new, separate scene history file.
            self.__history_writer = HistoryWriter(config_data)

        skip_preview_phase = (True if 'goal' in config_data and
                              'skip_preview_phase' in config_data['goal']
                              else False)
        if self.__debug_to_terminal:
            if config_data['name']:
                print("STARTING NEW SCENE: " + config_data['name'])
            else:
                print("STARTING NEW SCENE")
            if self._metadata_tier:
                print("METADATA TIER: " + self._metadata_tier)
            else:
                print("METADATA TIER: DEFAULT (NOT CONFIGURED)")
            print("STEP: 0")
            print("ACTION: Initialize")

        if (self.__debug_to_file or self._config.get(
                self.CONFIG_EVALUATION, False)) \
                and config_data['name'] is not None:
            os.makedirs('./' + config_data['name'], exist_ok=True)
            self.__output_folder = './' + config_data['name'] + '/'
            file_list = glob.glob(self.__output_folder + '*')
            for file_path in file_list:
                os.remove(file_path)

        if self._config.get(self.CONFIG_EVALUATION, False):
            team = self._config.get(self.CONFIG_TEAM, '')
            scene = self.__scene_configuration.get(
                'name', '').replace('json', '')
            self.__plotter = TopDownPlotter(
                team, scene, self.__screen_width, self.__screen_height)
            self._create_video_recorders()

        pre_restrict_output = self.wrap_output(self._controller.step(
            self.wrap_step(action='Initialize', sceneConfig=config_data)))

        output = self.restrict_step_output_metadata(pre_restrict_output)

        if not skip_preview_phase:
            if (self._goal is not None and
                    self._goal.last_preview_phase_step > 0):
                image_list = output.image_list
                depth_map_list = output.depth_map_list
                object_mask_list = output.object_mask_list

                if self.__debug_to_terminal:
                    print('STARTING PREVIEW PHASE...')

                for i in range(0, self._goal.last_preview_phase_step):
                    output = self.step('Pass')
                    image_list = image_list + output.image_list
                    depth_map_list = depth_map_list + output.depth_map_list
                    object_mask_list = (object_mask_list +
                                        output.object_mask_list)

                if self.__debug_to_terminal:
                    print('ENDING PREVIEW PHASE')

                if self._config.get(self.CONFIG_EVALUATION, False):
                    self.__image_recorder.add(image_list[0])

                output.image_list = image_list
                output.depth_map_list = depth_map_list
                output.object_mask_list = object_mask_list
            elif self.__debug_to_terminal:
                print('NO PREVIEW PHASE')

        return output

    # TODO: may need to reevaluate validation strategy/error handling in the
    # future
    """
    Need a validation/conversion step for what ai2thor will accept as input
    to keep parameters more simple for the user (in this case, wrapping
    rotation degrees into an object)
    """

    def validate_and_convert_params(self, action, **kwargs):
        moveMagnitude = MOVE_DISTANCE
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

        if not Util.is_number(amount, self.AMOUNT_KEY):
            # The default for open/close is 1, the default for "Move" actions
            # is 0.5
            if action in self.OBJECT_MOVE_ACTIONS:
                amount = self.DEFAULT_OBJECT_MOVE_AMOUNT
            else:
                amount = self.DEFAULT_AMOUNT

        if not Util.is_number(force, self.FORCE_KEY):
            force = self.DEFAULT_FORCE

        # Check object directions are numbers
        if not Util.is_number(
                objectImageCoordsX,
                self.OBJECT_IMAGE_COORDS_X_KEY):
            objectImageCoordsX = self.DEFAULT_IMG_COORD

        if not Util.is_number(
                objectImageCoordsY,
                self.OBJECT_IMAGE_COORDS_Y_KEY):
            objectImageCoordsY = self.DEFAULT_IMG_COORD

        # Check receptacle directions are numbers
        if not Util.is_number(
                receptacleObjectImageCoordsX,
                self.RECEPTACLE_IMAGE_COORDS_X_KEY):
            receptacleObjectImageCoordsX = self.DEFAULT_IMG_COORD

        if not Util.is_number(
                receptacleObjectImageCoordsY,
                self.RECEPTACLE_IMAGE_COORDS_Y_KEY):
            receptacleObjectImageCoordsY = self.DEFAULT_IMG_COORD

        amount = Util.is_in_range(
            amount,
            self.MIN_AMOUNT,
            self.MAX_AMOUNT,
            self.DEFAULT_AMOUNT,
            self.AMOUNT_KEY)
        force = Util.is_in_range(
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
            moveMagnitude = MOVE_DISTANCE

        # Add in noise if noise is enable
        if self.__enable_noise:
            rotation = rotation * (1 + self.generate_noise())
            horizon = horizon * (1 + self.generate_noise())
            moveMagnitude = moveMagnitude * (1 + self.generate_noise())

        rotation_vector = {}
        rotation_vector['y'] = rotation

        object_vector = {}
        object_vector['x'] = objectImageCoordsX
        object_vector['y'] = self._convert_y_image_coord_for_unity(
            objectImageCoordsY)

        receptacle_vector = {}
        receptacle_vector['x'] = receptacleObjectImageCoordsX
        receptacle_vector['y'] = self._convert_y_image_coord_for_unity(
            receptacleObjectImageCoordsY)

        return dict(
            objectId=kwargs.get("objectId", None),
            receptacleObjectId=kwargs.get("receptacleObjectId", None),
            rotation=rotation_vector,
            horizon=horizon,
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

        if self.__history_enabled and self.__step_number > 0:
            self.__history_writer.add_step(self.__history_item)

        if (self._goal.last_step is not None and
                self._goal.last_step == self.__step_number):
            print(
                "MCS Warning: You have passed the last step for this scene. " +
                "Ignoring your action. Please call controller.end_scene() " +
                "now.")
            return None

        if ',' in action:
            action, kwargs = Util.input_to_action_and_params(action)

        action_list = self.retrieve_action_list(self._goal, self.__step_number)
        if action not in action_list:
            print(
                "MCS Warning: The given action '" +
                action +
                "' is not valid. Ignoring your action. " +
                "Please call controller.step() with a valid action.")
            print("Actions (Step " + str(self.__step_number) + "): " +
                  ", ".join(action_list))
            return None

        self.__step_number += 1

        if self.__debug_to_terminal:
            print("================================================" +
                  "===============================")
            print("STEP: " + str(self.__step_number))
            print("ACTION: " + action)
            if self._goal.habituation_total >= self.__habituation_trial:
                print("HABITUATION TRIAL: " + str(self.__habituation_trial) +
                      " / " + str(self._goal.habituation_total))
            elif self._goal.habituation_total > 0:
                print("HABITUATION TRIAL: DONE")
            else:
                print("HABITUATION TRIAL: NONE")

        params = self.validate_and_convert_params(action, **kwargs)

        # Only call mcs_action_to_ai2thor_action AFTER calling
        # validate_and_convert_params
        action = self.mcs_action_to_ai2thor_action(action)

        if (action == 'EndHabituation'):
            self.__habituation_trial += 1

        if (self._goal.last_step is not None and
                self._goal.last_step == self.__step_number):
            print(
                "MCS Warning: This is your last step for this scene. All " +
                "your future actions will be skipped. Please call " +
                "controller.end_scene() now.")

        pre_restrict_output = self.wrap_output(self._controller.step(
            self.wrap_step(action=action, **params)))

        history_copy = copy.deepcopy(pre_restrict_output)
        del history_copy.depth_map_list
        del history_copy.image_list
        del history_copy.object_mask_list
        self.__history_item = SceneHistory(
            step=self.__step_number,
            action=action,
            args=kwargs,
            params=params,
            output=history_copy)

        output = self.restrict_step_output_metadata(pre_restrict_output)

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
            The selected choice required by the end of scenes with
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

        # add history step prediction attributes before add to the writer
        # in the next step
        if self.__history_item is not None:
            self.__history_item.classification = choice
            self.__history_item.confidence = confidence
            self.__history_item.violations_xy_list = violations_xy_list
            self.__history_item.internal_state = internal_state

        if(heatmap_img is not None and
           isinstance(heatmap_img, PIL.Image.Image) and
           self._config[self.CONFIG_EVALUATION]):
            self.__heatmap_recorder.add(heatmap_img)

    def generate_time(self):
        return datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

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

    def read_config_file(self):
        if os.path.exists(self._config_file):
            with open(self._config_file, 'r') as config_file:
                config = yaml.load(config_file)
                if self.__debug_to_terminal:
                    print('Read MCS Config File:')
                    print(config)
                if self.CONFIG_METADATA_TIER not in config:
                    config[self.CONFIG_METADATA_TIER] = ''
                if self.CONFIG_EVALUATION not in config:
                    config[self.CONFIG_EVALUATION] = False
                return config
        return {}

    def update_goal_target_image(self, goal_output):
        target_name_list = ['target', 'target_1', 'target_2']

        for target_name in target_name_list:
            # need to convert goal image data from string to array
            if (
                target_name in goal_output.metadata and
                'image' in goal_output.metadata[target_name] and
                isinstance(goal_output.metadata[target_name]['image'], str)
            ):
                image_list_string = goal_output.metadata[target_name]['image']
                goal_output.metadata[target_name]['image'] = np.array(
                    ast.literal_eval(image_list_string)).tolist()

        return goal_output

    def restrict_step_output_metadata(self, step_output):
        # Use this function to filter out of the step output any data
        # that shouldn't be returned at certain metadata tiers
        if(self._metadata_tier == self.CONFIG_METADATA_TIER_LEVEL_1):
            step_output.object_mask_list = []

        if (
            self._metadata_tier == self.CONFIG_METADATA_TIER_LEVEL_1 or
            self._metadata_tier == self.CONFIG_METADATA_TIER_LEVEL_2
        ):
            step_output.position = None
            step_output.rotation = None
            step_output.structural_object_list = []
            step_output.object_list = []

            # Below is to remove the goal targets from output
            target_name_list = ['target', 'target_1', 'target_2']

            for target_name in target_name_list:
                if (
                    target_name in step_output.goal.metadata and
                    'image' in step_output.goal.metadata[target_name]
                ):
                    step_output.goal.metadata[target_name]['image'] = None

        return step_output

    def retrieve_action_list(self, goal, step_number):
        if goal is not None and goal.action_list is not None:
            if step_number < goal.last_preview_phase_step:
                return ['Pass']
            adjusted_step = step_number - goal.last_preview_phase_step
            if len(goal.action_list) > adjusted_step:
                if len(goal.action_list[adjusted_step]) > 0:
                    return goal.action_list[adjusted_step]

        return self.ACTION_LIST

    def retrieve_goal(self, scene_configuration):
        goal_config = (
            scene_configuration['goal']
            if 'goal' in scene_configuration
            else {}
        )

        if 'category' in goal_config:
            # Backwards compatibility
            goal_config['metadata']['category'] = goal_config['category']

        return self.update_goal_target_image(GoalMetadata(
            action_list=goal_config.get('action_list', None),
            category=goal_config.get('category', ''),
            description=goal_config.get('description', ''),
            habituation_total=goal_config.get('habituation_total', 0),
            last_preview_phase_step=(
                goal_config.get('last_preview_phase_step', 0)
            ),
            last_step=goal_config.get('last_step', None),
            metadata=goal_config.get('metadata', {})
        ))

    def retrieve_head_tilt(self, scene_event):
        return scene_event.metadata['agent']['cameraHorizon']

    def retrieve_rotation(self, scene_event):
        return scene_event.metadata['agent']['rotation']['y']

    def retrieve_object_colors(self, scene_event):
        # Use the color map for the final event (though they should all be the
        # same anyway).
        return scene_event.events[len(
            scene_event.events) - 1].object_id_to_color

    def retrieve_object_list(self, scene_event):
        # Return object lis for all tier levels, the restrict output function
        # will then strip out the necessary metadata
        if (self._metadata_tier == self.CONFIG_METADATA_TIER_LEVEL_1 or
                self._metadata_tier == self.CONFIG_METADATA_TIER_LEVEL_2 or
                self._metadata_tier == self.CONFIG_METADATA_TIER_ORACLE):
            return sorted(
                [
                    self.retrieve_object_output(
                        object_metadata,
                        self.retrieve_object_colors(scene_event),
                    )
                    for object_metadata in scene_event.metadata['objects']
                ],
                key=lambda x: x.uuid
            )
        else:
            # if no config specified, return visible objects (for now)
            return sorted(
                [
                    self.retrieve_object_output(
                        object_metadata,
                        self.retrieve_object_colors(scene_event)
                    )
                    for object_metadata in scene_event.metadata['objects']
                    if object_metadata['visibleInCamera'] or
                    object_metadata['isPickedUp']
                ],
                key=lambda x: x.uuid
            )

    def retrieve_object_output(self, object_metadata, object_id_to_color):
        material_list = (
            list(
                filter(
                    Util.verify_material_enum_string,
                    [
                        material.upper()
                        for material in object_metadata['salientMaterials']
                    ],
                )
            )
            if object_metadata['salientMaterials'] is not None
            else []
        )

        rgb = (
            object_id_to_color[object_metadata['objectId']]
            if object_metadata['objectId'] in object_id_to_color
            else [None, None, None]
        )

        bounds = (
            object_metadata['objectBounds']
            if 'objectBounds' in object_metadata and
            object_metadata['objectBounds'] is not None
            else {}
        )

        return (
            ObjectMetadata(
                uuid=object_metadata['objectId'],
                color={'r': rgb[0], 'g': rgb[1], 'b': rgb[2]},
                dimensions=(
                    bounds['objectBoundsCorners']
                    if 'objectBoundsCorners' in bounds
                    else None
                ),
                direction=object_metadata['direction'],
                distance=(
                    object_metadata['distanceXZ'] / MOVE_DISTANCE
                ),  # DEPRECATED
                distance_in_steps=(
                    object_metadata['distanceXZ'] / MOVE_DISTANCE
                ),
                distance_in_world=(object_metadata['distance']),
                held=object_metadata['isPickedUp'],
                mass=object_metadata['mass'],
                material_list=material_list,
                position=object_metadata['position'],
                rotation=object_metadata['rotation'],
                shape=object_metadata['shape'],
                texture_color_list=object_metadata['colorsFromMaterials'],
                visible=(
                    object_metadata['visibleInCamera'] or
                    object_metadata['isPickedUp']
                ),
            )
        )

    def retrieve_pose(self, scene_event) -> str:
        pose = Pose.UNDEFINED.name

        try:
            pose = Pose[scene_event.metadata['pose']].name
        except KeyError:
            print(
                "Pose " +
                scene_event.metadata['pose'] +
                " is not currently supported.")
        finally:
            return pose

    def retrieve_position(self, scene_event) -> dict:
        return scene_event.metadata['agent']['position']

    def retrieve_return_status(self, scene_event):
        # TODO MCS-47 Need to implement all proper step statuses on the Unity
        # side
        return_status = ReturnStatus.UNDEFINED.name

        try:
            if scene_event.metadata['lastActionStatus']:
                return_status = ReturnStatus[
                    scene_event.metadata['lastActionStatus']
                ].name
        except KeyError:
            print(
                "Return status " +
                scene_event.metadata['lastActionStatus'] +
                " is not currently supported.")
        finally:
            return return_status

    def retrieve_structural_object_list(self, scene_event):
        # Return structural for all tier levels, the restrict output function
        # will then strip out the necessary metadata
        if (self._metadata_tier == self.CONFIG_METADATA_TIER_LEVEL_1 or
                self._metadata_tier == self.CONFIG_METADATA_TIER_LEVEL_2 or
                self._metadata_tier == self.CONFIG_METADATA_TIER_ORACLE):
            return sorted(
                [
                    self.retrieve_object_output(
                        object_metadata,
                        self.retrieve_object_colors(scene_event),
                    )
                    for object_metadata in scene_event.metadata[
                        'structuralObjects'
                    ]
                ],
                key=lambda x: x.uuid
            )
        else:
            # if no config specified, return visible structural objects (for
            # now)
            return sorted(
                [
                    self.retrieve_object_output(
                        object_metadata, self.retrieve_object_colors(
                            scene_event)
                    )
                    for object_metadata in scene_event.metadata[
                        'structuralObjects'
                    ]
                    if object_metadata['visibleInCamera']
                ],
                key=lambda x: x.uuid
            )

    def save_images(self, scene_event, max_depth):
        image_list = []
        depth_map_list = []
        object_mask_list = []

        for index, event in enumerate(scene_event.events):
            scene_image = PIL.Image.fromarray(event.frame)
            image_list.append(scene_image)

            if self._config.get(self.CONFIG_EVALUATION, False):
                self.__image_recorder.add(scene_image)
                self.__topdown_recorder.add(
                    self.__plotter.plot(scene_event, self.__step_number))

            if self.__depth_maps:
                # The Unity depth array (returned by Depth.shader) contains
                # a third of the total max depth in each RGB element.
                unity_depth_array = event.depth_frame.astype(np.float32)
                # Convert to values between 0 and max_depth for output.
                depth_float_array = (
                    (unity_depth_array[:, :, 0] * (max_depth / 3.0) / 255.0) +
                    (unity_depth_array[:, :, 1] * (max_depth / 3.0) / 255.0) +
                    (unity_depth_array[:, :, 2] * (max_depth / 3.0) / 255.0)
                )
                # Convert to pixel values for saving debug image.
                depth_pixel_array = depth_float_array * 255 / max_depth
                depth_map = PIL.Image.fromarray(
                    depth_pixel_array.astype(np.uint8)
                )
                if self._config.get(self.CONFIG_EVALUATION, False):
                    self.__depth_recorder.add(depth_map)
                depth_map_list.append(np.array(depth_float_array))

            if self.__object_masks:
                object_mask = PIL.Image.fromarray(
                    event.instance_segmentation_frame)
                object_mask_list.append(object_mask)
                if self._config.get(self.CONFIG_EVALUATION, False):
                    self.__segmentation_recorder.add(object_mask)

            if self.__debug_to_file and self.__output_folder is not None:
                step_plus_substep_index = 0 if self.__step_number == 0 else (
                    ((self.__step_number - 1) * len(scene_event.events)) +
                    (index + 1)
                )
                suffix = '_' + str(step_plus_substep_index) + '.png'
                scene_image.save(fp=self.__output_folder +
                                 'frame_image' + suffix)
                if self.__depth_maps:
                    depth_map.save(fp=self.__output_folder +
                                   'depth_map' + suffix)
                if self.__object_masks:
                    object_mask.save(fp=self.__output_folder +
                                     'object_mask' + suffix)

        return image_list, depth_map_list, object_mask_list

    def wrap_output(self, scene_event):
        if self.__debug_to_file and self.__output_folder is not None:
            with open(self.__output_folder + 'ai2thor_output_' +
                      str(self.__step_number) + '.json', 'w') as json_file:
                json.dump({
                    "metadata": scene_event.metadata
                }, json_file, sort_keys=True, indent=4)

        image_list, depth_map_list, object_mask_list = self.save_images(
            scene_event,
            scene_event.metadata.get(
                'clippingPlaneFar',
                self.DEFAULT_CLIPPING_PLANE_FAR
            )
        )

        objects = scene_event.metadata.get('objects', None)
        agent = scene_event.metadata.get('agent', None)
        step_output = StepMetadata(
            action_list=self.retrieve_action_list(
                self._goal, self.__step_number),
            camera_aspect_ratio=(self.__screen_width, self.__screen_height),
            camera_clipping_planes=(
                scene_event.metadata.get('clippingPlaneNear', 0.0),
                scene_event.metadata.get('clippingPlaneFar', 0.0),
            ),
            camera_field_of_view=scene_event.metadata.get('fov', 0.0),
            camera_height=scene_event.metadata.get(
                'cameraPosition', {}).get('y', 0.0),
            depth_map_list=depth_map_list,
            goal=self._goal,
            habituation_trial=(
                self.__habituation_trial
                if self._goal.habituation_total >= self.__habituation_trial
                else None
            ),
            head_tilt=self.retrieve_head_tilt(scene_event),
            image_list=image_list,
            object_list=self.retrieve_object_list(scene_event),
            object_mask_list=object_mask_list,
            pose=self.retrieve_pose(scene_event),
            position=self.retrieve_position(scene_event),
            return_status=self.retrieve_return_status(scene_event),
            reward=Reward.calculate_reward(
                self._goal, objects, agent, self.__step_number),
            rotation=self.retrieve_rotation(scene_event),
            step_number=self.__step_number,
            structural_object_list=self.retrieve_structural_object_list(
                scene_event)
        )

        self.__head_tilt = step_output.head_tilt

        if self.__debug_to_terminal:
            print("RETURN STATUS: " + step_output.return_status)
            print("REWARD: " + str(step_output.reward))
            print("SELF METADATA:")
            print("  CAMERA HEIGHT: " + str(step_output.camera_height))
            print("  HEAD TILT: " + str(step_output.head_tilt))
            print("  POSITION: " + str(step_output.position))
            print("  ROTATION: " + str(step_output.rotation))
            print("OBJECTS: " + str(len(step_output.object_list)) + " TOTAL")
            if len(step_output.object_list) > 0:
                for line in Util.generate_pretty_object_output(
                        step_output.object_list):
                    print("    " + line)

        if self.__debug_to_file and self.__output_folder is not None:
            with open(self.__output_folder + 'mcs_output_' +
                      str(self.__step_number) + '.json', 'w') as json_file:
                json_file.write(str(step_output))

        return step_output

    def wrap_step(self, **kwargs):
        # whether or not to randomize segmentation mask colors
        consistentColors = False

        if(self._metadata_tier == self.CONFIG_METADATA_TIER_ORACLE):
            consistentColors = True

        # Create the step data dict for the AI2-THOR step function.
        step_data = dict(
            continuous=True,
            gridSize=self.GRID_SIZE,
            logs=True,
            renderDepthImage=self.__depth_maps,
            renderObjectImage=self.__object_masks,
            snapToGrid=False,
            # Yes, in AI2-THOR, the player's reach appears to be
            # governed by the "visibilityDistance", confusingly...
            visibilityDistance=MAX_REACH_DISTANCE,
            consistentColors=consistentColors,
            **kwargs
        )

        if self.__debug_to_file and self.__output_folder is not None:
            with open(self.__output_folder + 'ai2thor_input_' +
                      str(self.__step_number) + '.json', 'w') as json_file:
                json.dump(step_data, json_file, sort_keys=True, indent=4)

        return step_data

    def generate_noise(self):
        """
        Returns a random value between -0.05 and 0.05 used to add noise to all
        numerical action parameters enable_noise is True.
        Returns
        -------
        float
            A value between -0.05 and 0.05 (using random.uniform).
        """

        return random.uniform(-0.5, 0.5)
