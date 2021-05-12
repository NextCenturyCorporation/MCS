from abc import ABC

import enum
import datetime
import PIL
from typing import Dict, List
from .config_manager import ConfigManager, SceneConfiguration
from .goal_metadata import GoalMetadata


class EventType(enum.Enum):
    '''
    Enum for the possible events the controller can send to subscribers
    '''
    ON_INIT = enum.auto()
    ON_START_SCENE = enum.auto()
    ON_BEFORE_STEP = enum.auto()
    ON_AFTER_STEP = enum.auto()
    ON_PREDICTION = enum.auto()
    ON_END_SCENE = enum.auto()


class BaseEventPayload:

    def __init__(self, step_number: int):
        self.step_number = step_number


class ControllerEventPayload(BaseEventPayload):
    '''
    Payload class for controller events.  This class will be redone soon.
    '''

    def __init__(self, output_folder: str, config: ConfigManager,
                 step_number: int, scene_config: SceneConfiguration,
                 habituation_trial: int, goal: Dict):
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        self.output_folder = output_folder
        self.config = config
        self.step_number = step_number
        self.scene_config = scene_config
        self.habituation_trial = habituation_trial
        self.goal = goal

    def get_output_folder(self) -> str:
        return self.output_folder

    def get_config(self) -> ConfigManager:
        return self.config

    def get_timestamp(self) -> str:
        return self.timestamp

    def get_step_number(self) -> int:
        return self.step_number

    def get_scene_config(self) -> SceneConfiguration:
        self.scene_configuration

    def get_habituation_trial(self) -> int:
        return self.habituation_trial

    def get_goal(self) -> GoalMetadata:
        return self.goal


class PredictionPayload(BaseEventPayload):
    '''
        Class that contains relevant data to controller subscribers
        When the prediction event occurs.
    '''

    def __init__(self, config, choice: str = None,
                 confidence: float = None,
                 violations_xy_list: List[Dict[str, float]] = None,
                 heatmap_img: PIL.Image.Image = None,
                 internal_state: object = None):
        self.config = config
        self.choice = choice
        self.confidence = confidence
        self.violations_xy_list = violations_xy_list
        self.heatmap_img = heatmap_img
        self.internal_state = internal_state


class AbstractControllerSubscriber(ABC):
    '''
    Abstract class for controller event subscribers.  Subscriber
    implementations should override at least one of the event classes.
    '''

    def __init__(self):
        self._switcher = {
            EventType.ON_INIT: self.on_init,
            EventType.ON_START_SCENE: self.on_start_scene,
            EventType.ON_BEFORE_STEP: self.on_before_step,
            EventType.ON_AFTER_STEP: self.on_after_step,
            EventType.ON_PREDICTION: self.on_prediction,
            EventType.ON_END_SCENE: self.on_end_scene
        }

    def on_event(self, type: EventType,
                 payload: ControllerEventPayload, controller):
        self._switcher.get(
            type,
            "default")(
            payload,
            controller)

    def on_init(self, payload: ControllerEventPayload, controller):
        pass

    def on_start_scene(self, payload: ControllerEventPayload, controller):
        pass

    def on_before_step(self, payload: ControllerEventPayload, controller):
        pass

    def on_after_step(self, payload: ControllerEventPayload, controller):
        pass

    def on_prediction(self, payload: PredictionPayload, controller):
        pass

    def on_end_scene(self, payload: ControllerEventPayload, controller):
        pass
