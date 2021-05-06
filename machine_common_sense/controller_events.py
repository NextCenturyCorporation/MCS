from abc import ABC

import enum
import PIL
from typing import Dict, List


class EventType(enum.Enum):
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
    def __init__(self):
        pass


class PredictionPayload(BaseEventPayload):

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

    def on_init(self, payload, controller):
        pass

    def on_start_scene(self, payload, controller):
        pass

    def on_before_step(self, payload, controller):
        pass

    def on_after_step(self, payload, controller):
        pass

    def on_prediction(self, payload: PredictionPayload, controller):
        pass

    def on_end_scene(self, payload, controller):
        pass
