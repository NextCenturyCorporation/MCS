import atexit
import contextlib
import datetime
import glob
import io
import json
import logging
import os
from typing import Dict, List, Optional, Union

import ai2thor.controller
import ai2thor.server
import numpy as np
import typeguard  # can we replace with pydantic function validator?

logger = logging.getLogger(__name__)


# How far the player can reach.  I think this value needs to be bigger
# than the MAX_MOVE_DISTANCE or else the player may not be able to move
# into a position to reach some objects (it may be mathematically impossible).
DEFAULT_MOVE = 0.1

from .action import Action
from .config_manager import ConfigManager, SceneConfiguration
from .controller_events import (AfterStepPayload, BeforeStepPayload,
                                EndScenePayload, EventType, StartScenePayload)
from .controller_output_handler import ControllerOutputHandler
from .goal_metadata import GoalMetadata
from .parameter import Parameter, compare_param_values, rebuild_endhabituation
from .step_metadata import StepMetadata


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
    return ai2thor.server.read_buffer_image(
        image_depth_data,
        self.screen_width,
        self.screen_height,
        dtype=np.float32
    )


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
    unity_app_file_path: str
    config: ConfigManager
    """

    @typeguard.typechecked
    def __init__(self, unity_app_file_path: str, config: ConfigManager):

        # Suppress print statements from the AI2-THOR Controller's constructor.
        with contextlib.redirect_stdout(io.StringIO()) as _:
            self._controller = ai2thor.controller.Controller(
                quality='Medium',
                fullscreen=False,
                headless=False,  # TODO confirm functionality
                local_executable_path=unity_app_file_path,
                width=config.get_screen_width(),
                height=config.get_screen_height(),
                scene='MCS',  # Unity scene name
                logs=True,
                # This constructor always initializes a scene, so add a scene
                # config to ensure it doesn't error
                sceneConfig={
                    "objects": []
                }
            )

        if not self._controller:
            raise Exception('AI2-THOR/Unity Controller failed to initialize')

        self._on_init()
        self._set_config(config)

    def _on_init(self):
        '''Set class variables after controller is initialized'''
        self._subscribers = []
        self._failure_handler_registered = False
        self._end_scene_called = False
        self._goal = GoalMetadata()
        self.__habituation_trial = 1
        # Output folder used to save debug image, video, and JSON files.
        self.__output_folder = None
        self._scene_config = None
        self.__step_number = 0

    def _set_config(self, config: ConfigManager):
        '''Allows config to be changed without changing the controller and
        attached Unity process.  This typically should only be called by the
        MCS package itself.

        For users, call machine_common_sense.change_config()
        '''
        self._config = config
        self._output_handler = ControllerOutputHandler(self._config)
        self.parameter_converter = Parameter(config)

    @typeguard.typechecked
    def start_scene(
        self, config_data: Union[SceneConfiguration, Dict]) \
            -> StepMetadata:
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
        self.__steps_in_lava = 0
        self._goal = self._scene_config.retrieve_goal(
            self._config.get_steps_allowed_in_lava())
        self._end_scene_called = False

        skip_preview_phase = (scene_config.goal is not None and
                              scene_config.goal.skip_preview_phase)

        if (not self._scene_config.name):
            raise Exception('The `name` field in the scene '
                            'file cannot be empty.')

        if (self._config.is_file_writing_enabled()):
            os.makedirs(f'./{scene_config.name}', exist_ok=True)
            self.__output_folder = f'./{scene_config.name}/'
            file_list = glob.glob(f'{self.__output_folder}*')
            for file_path in file_list:
                os.remove(file_path)

        sc = scene_config.dict(exclude_none=True, by_alias=True)

        ai2thor_step = self.parameter_converter.wrap_step(
            action='Initialize', sceneConfig=sc)
        step_output = self._controller.step(ai2thor_step)

        self._output_handler.set_scene_config(scene_config)
        (pre_restrict_output, output) = self._output_handler.handle_output(
            step_output, self._goal, self.__step_number,
            self.__habituation_trial)

        self.__steps_in_lava = output.steps_on_lava

        if not skip_preview_phase:
            if (self._goal is not None and
                    self._goal.last_preview_phase_step > 0):
                image_list = output.image_list
                depth_map_list = output.depth_map_list
                object_mask_list = output.object_mask_list

                logger.debug('STARTING PREVIEW PHASE...')

                for _ in range(self._goal.last_preview_phase_step):
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
            if(self._failure_handler_registered is False and
                    self._config.is_history_enabled()):
                # make sure history file is written when program exits
                atexit.register(self.end_scene, rating=None, score=-1)
                self._failure_handler_registered = True

        payload = self._create_post_step_event_payload_kwargs(
            ai2thor_step, step_output, pre_restrict_output, output)
        start_scene_payload = StartScenePayload(**payload)
        self._publish_event(
            EventType.ON_START_SCENE, start_scene_payload)

        return output

    def _convert_scene_config(self, config_data) -> SceneConfiguration:
        if isinstance(config_data, SceneConfiguration):
            return config_data
        return SceneConfiguration(**config_data)

    @typeguard.typechecked
    def step(self, action: str, **kwargs) -> Optional[StepMetadata]:
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

        Raises
        ------
            ValueError: If values are outside acceptable ranges or unable to
                convert to a number.
        """
        if (self._goal.last_step is not None and
                self._goal.last_step == self.__step_number):
            logger.error(
                "You have passed the last step for this scene. "
                "Ignoring your action. Please call controller.end_scene() "
                "now.")
            return None

        # if they call end scene action they should have
        #   called end_scene instead of step
        if action == Action.END_SCENE.value:
            self.end_scene()
            raise SystemExit(0)

        # reformulate hidden EndHabituation parameters
        if action == Action.END_HABITUATION.value:
            step_action_list = \
                self._goal._retrieve_unfiltered_action_list(self.__step_number)
            action = rebuild_endhabituation(step_action_list)

        if ',' in action:
            action, kwargs = Action.input_to_action_and_params(action)

        action_list = self._goal.retrieve_action_list_at_step(
            self.__step_number, self.__steps_in_lava)

        # Only continue with this action step if the given action and
        # parameters are in the restricted action list.
        continue_with_step = any(action == restricted_action and (
            len(restricted_params.items()) == 0 or all(
                compare_param_values(restricted_params.get(key), value)
                for key, value in kwargs.items()
            )
        ) for restricted_action, restricted_params in action_list)

        if not continue_with_step:
            logger.error(
                f"The given action '{action}' with parameters "
                f"'{kwargs}' isn't in the action_list. Ignoring your action. "
                f"Possible actions at step {self.__step_number}:"
            )
            for action_data in action_list:
                logger.error(f'    {action_data}')
            raise ValueError(f"{action}-{kwargs} not in {action_list}")

        self.__step_number += 1

        payload = self._create_event_payload_kwargs()
        payload['action'] = action
        payload['habituation_trial'] = self.__habituation_trial
        payload['goal'] = self._goal
        self._publish_event(
            EventType.ON_BEFORE_STEP,
            BeforeStepPayload(**payload))

        if (action == Action.END_HABITUATION.value):
            self.__habituation_trial += 1

        if (self._goal.last_step is not None and
                self._goal.last_step == self.__step_number):
            logger.warning(
                "This is your last step for this scene. All "
                "your future actions will be skipped. Please call "
                "controller.end_scene() now.")

        ai2thor_step, params = self.parameter_converter.build_ai2thor_step(
            action=action, **kwargs)
        step_output = self._controller.step(ai2thor_step)

        (pre_restrict_output, output) = self._output_handler.handle_output(
            step_output, self._goal, self.__step_number,
            self.__habituation_trial)

        self.__steps_in_lava = output.steps_on_lava

        payload = self._create_post_step_event_payload_kwargs(
            ai2thor_step, step_output, pre_restrict_output, output)
        payload['ai2thor_action'] = action
        payload['step_params'] = params
        payload['action_kwargs'] = kwargs
        self._publish_event(
            EventType.ON_AFTER_STEP,
            AfterStepPayload(**payload))

        return output

    @typeguard.typechecked
    def end_scene(
        self,
        rating: Optional[float] = None,
        score: Optional[float] = None,
        report: Dict[int, object] = None
    ) -> None:
        """
        Ends the current scene.  Calling end_scene() before calling
        start_scene() will do nothing. Calling end_scene() twice with
        the same scene will throw an exception.

        Parameters
        ----------
        rating : float, optional
            The plausibility rating to classify a passive / VoE scene as either
            plausible or implausible. Not used for any interactive scenes. For
            passive agent scenes, this rating should be continuous, from 0.0
            (completely implausible) to 1.0 (completely plausible). For other
            passive scenes, this rating must be binary, either 0 (implausible)
            or 1 (plausible). End-of-scene ratings are
            required for all passive / VoE scenes. (default None)
        score : float, optional
            The continuous plausibility score between 0.0 (completely
            implausible) and 1.0 (completely plausible). End-of-scene scores
            are required for all passive / VoE scenes except agent scenes.
            Not used for any interactive scenes or passive agent scenes.
            (default None)

            Note: when an issue causes the program to exit prematurely or
            end_scene isn't properly called but history_enabled is true,
            this value will be written to file as -1.
        report : Dict[int, object], optional
            Variable for retrospective per frame reporting for passive / VoE
            scenes. Not used for any interactive scenes or passive agent
            scenes. (default None)

            Key is an int representing a step/frame number from output step
            metadata, starting at 1. Value or payload contains:

                * rating : float or int, optional
                    The plausibility rating to classify a passive / VoE scene
                    as either plausible or implausible. Not used for any
                    interactive scenes. For passive agent scenes, this rating
                    should be continuous, from 0.0 (completely implausible) to
                    1.0 (completely plausible). For other passive scenes, this
                    rating must be binary, either 0 (implausible) or 1
                    (plausible). Frame-by-frame ratings are no
                    longer required for any scenes (but end-of-scene ratings
                    are). (default None)
                * score : float, optional
                    The continuous plausibility score between 0.0 (completely
                    implausible) and 1.0 (completely plausible). Frame-by-frame
                    scores are required for all passive / VoE scenes except
                    agent scenes. Not used for any interactive scenes or
                    passive agent scenes. (default None)
                * violations_xy_list : List[Dict[str, float]], optional
                    A list of one or more (x, y) locations
                    (ex: [{"x": 1, "y": 3.4}]), each representing a potential
                    violation-of-expectation. These locations are required for
                    all passive / VoE scenes except agent scenes. Not used for
                    any interactive scenes or passive agent scenes.
                    (default None)
                * internal_state : object, optional
                    A properly formatted json object representing various kinds
                    of internal states at a particular moment. Examples include
                    the estimated position of the agent, current map of the
                    world, etc. (default None)

            Example report:

            {

                    1: {

                        "rating": 1,

                        "score": 0.75,

                        "violations_xy_list": [{"x": 1,"y": 1}],

                        "internal_state": {"test": "some state"}

                    }

            }

        """
        if(not self._end_scene_called):
            payload = self._create_event_payload_kwargs()
            payload['rating'] = rating
            payload['score'] = score
            payload['report'] = report

            self._publish_event(
                EventType.ON_END_SCENE,
                EndScenePayload(
                    **payload))
            self._end_scene_called = True
        else:
            raise RuntimeError("end_scene called twice with the same scene")

        if (self._failure_handler_registered):
            atexit.unregister(self.end_scene)
            self._failure_handler_registered = False

    @typeguard.typechecked
    def stop_simulation(self) -> None:
        """Stop the 3D simulation environment. This controller won't work any
        more."""
        self._controller.stop()

    @typeguard.typechecked
    def get_metadata_level(self) -> str:
        """
        Returns the current metadata level set in the config. If none
        specified, returns 'default'.

        Returns
        -------
        string
            A string containing the current metadata level.
        """
        return self._config.get_metadata_tier().value

    def retrieve_action_list_at_step(self, goal, step_number):
        return goal.retrieve_action_list_at_step(step_number)

    @typeguard.typechecked
    def retrieve_object_states(self, object_id: str) -> List:
        """Return the state list at the current step for the object with the
        given ID from the scene configuration data, if any."""
        return self._scene_config.retrieve_object_states(
            object_id,
            self.__step_number)

    def subscribe(self, subscriber):
        if subscriber not in self._subscribers:
            self._subscribers.append(subscriber)

    def remove_all_event_handlers(self):
        self._subscribers = []

    @typeguard.typechecked
    def _publish_event(self, event_type: EventType,
                       payload: Union[StartScenePayload, BeforeStepPayload,
                                      AfterStepPayload,
                                      EndScenePayload]):
        for subscriber in self._subscribers:
            try:
                subscriber.on_event(event_type, payload)
            except Exception as msg:
                logger.error(
                    f"Error in event with type={event_type}"
                    f" to subscriber={type(subscriber)}",
                    exc_info=msg)

    def _create_event_payload_kwargs(self) -> dict:
        return {"step_number": self.__step_number,
                "config": self._config,
                "scene_config": self._scene_config}

    def _create_post_step_event_payload_kwargs(
            self, wrapped_step, step_metadata, step_output: StepMetadata,
            restricted_step_output: StepMetadata) -> dict:
        args = self._create_event_payload_kwargs()
        args['output_folder'] = self.__output_folder
        args['timestamp'] = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        args['wrapped_step'] = wrapped_step
        args['step_metadata'] = step_metadata
        args['step_output'] = step_output
        args['restricted_step_output'] = restricted_step_output
        args['goal'] = self._goal
        return args
