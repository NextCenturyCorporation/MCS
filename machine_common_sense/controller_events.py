from abc import ABC

import enum


class EventType(enum.Enum):
    ON_INIT = 1
    ON_START_SCENE = 2
    ON_BEFORE_STEP = 3
    ON_AFTER_STEP = 4
    ON_END_SCENE = 5


class ControllerEventPayload():
    def __init__(self):
        self.step_number = 0


class AbstractControllerSubscriber(ABC):

    def __init__(self):
        self._switcher = {
            EventType.ON_INIT: self.on_init,
            EventType.ON_START_SCENE: self.on_start_scene,
            EventType.ON_BEFORE_STEP: self.on_before_step,
            EventType.ON_AFTER_STEP: self.on_after_step,
            EventType.ON_END_SCENE: self.on_end_scene,
            "default": self.on_default
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

    def on_end_scene(self, payload, controller):
        pass

    def on_default(self):
        pass
        # maybe log error?
