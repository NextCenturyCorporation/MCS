import datetime
import enum
from abc import ABC
from typing import Dict, Optional, Union

from ai2thor.server import Event, MultiAgentEvent

from .config_manager import BaseModel, ConfigManager, SceneConfiguration
from .goal_metadata import GoalMetadata
from .step_metadata import StepMetadata


class EventType(enum.Enum):
    '''
    Enum for the possible events the controller can send to subscribers
    '''
    ON_START_SCENE = enum.auto()
    ON_BEFORE_STEP = enum.auto()
    ON_AFTER_STEP = enum.auto()
    ON_END_SCENE = enum.auto()


class BaseEventPayload(BaseModel):
    step_number: int
    config: ConfigManager
    scene_config: Optional[SceneConfiguration]


class BasePostActionEventPayload(BaseEventPayload):
    output_folder: Optional[str]
    timestamp: str
    wrapped_step: dict
    step_metadata: Union[Event, MultiAgentEvent]
    step_output: StepMetadata
    restricted_step_output: StepMetadata
    goal: GoalMetadata


class StartScenePayload(BasePostActionEventPayload):
    ...


class AfterStepPayload(BasePostActionEventPayload):
    ai2thor_action: str
    step_params: dict
    action_kwargs: dict


class BeforeStepPayload(BaseEventPayload):
    action: str
    goal: GoalMetadata
    habituation_trial: Optional[int]


class EndScenePayload(BaseEventPayload):
    rating: Optional[str]
    score: Optional[float]
    report: Optional[dict]


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
        self.scene_config

    def get_habituation_trial(self) -> int:
        return self.habituation_trial

    def get_goal(self) -> GoalMetadata:
        return self.goal


class AbstractControllerSubscriber(ABC):
    '''
    Abstract class for controller event subscribers.  Subscriber
    implementations should override at least one of the event classes.
    '''

    def __init__(self):
        self._switcher = {
            EventType.ON_START_SCENE: self.on_start_scene,
            EventType.ON_BEFORE_STEP: self.on_before_step,
            EventType.ON_AFTER_STEP: self.on_after_step,
            EventType.ON_END_SCENE: self.on_end_scene
        }

    def on_event(self, type: EventType,
                 payload: ControllerEventPayload):
        self._switcher.get(
            type,
            "default")(
            payload)

    def on_start_scene(self, payload: StartScenePayload):
        pass

    def on_before_step(self, payload: BeforeStepPayload):
        pass

    def on_after_step(self, payload: AfterStepPayload):
        pass

    def on_end_scene(self, payload: EndScenePayload):
        pass
