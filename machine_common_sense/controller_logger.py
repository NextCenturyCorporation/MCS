import logging


from .event_type import EventType
from .controller_event_payload import ControllerEventPayload
from .util import Util

logger = logging.getLogger(__name__)


class ControllerLogger():

    def __init__(self):
        self._switcher = {
            EventType.ON_INIT: self.on_init,
            EventType.ON_START_SCENE: self.on_start_scene,
            EventType.ON_BEFORE_STEP: self.on_before_step,
            EventType.ON_AFTER_STEP: self.on_after_step,
            EventType.ON_END_SCENE: self.on_end_scene
        }

    def on_event(self, type: EventType,
                 payload: ControllerEventPayload, controller):
        logger.info(f"EventType: {type} Step: {payload.step_number}"
                    f" Payload: {payload}")
        self._switcher.get(type)(payload.step_number, payload, controller)

    def on_init(self, step_number: int, payload, controller):
        self._config = payload
        logger.info("init")

    def on_start_scene(self, step_number: int, payload, controller):
        # logger.info("start")
        logger.debug(
            "STARTING NEW SCENE: " +
            payload.scene_config.get(
                'name',
                ""))
        logger.debug(
            "METADATA TIER: " +
            payload.config.get_metadata_tier())
        logger.debug(f"STEP: {payload.step_number}")
        logger.debug("ACTION: Initialize")

        self._write_debug_output(payload)

    def on_before_step(self, step_number: int, payload, controller):
        logger.info("before step")
        logger.debug("================================================"
                     "===============================")
        logger.debug("STEP: " + str(step_number))
        logger.debug("ACTION: " + payload.action)
        if payload.goal.habituation_total >= payload.habituation_trial:
            logger.debug(f"HABITUATION TRIAL: "
                         f"{str(payload.habituation_trial)}"
                         f" / {str(payload.goal.habituation_total)}")
        elif payload.goal.habituation_total > 0:
            logger.debug("HABITUATION TRIAL: DONE")
        else:
            logger.debug("HABITUATION TRIAL: NONE")

    def on_after_step(self, step_number: int, payload, controller):
        self._write_debug_output(payload)

    def _write_debug_output(self, payload):
        step_output = payload.step_output
        logger.debug("RETURN STATUS: " + step_output.return_status)
        logger.debug("REWARD: " + str(step_output.reward))
        logger.debug("SELF METADATA:")
        logger.debug("  CAMERA HEIGHT: " + str(step_output.camera_height))
        logger.debug("  HEAD TILT: " + str(step_output.head_tilt))
        logger.debug("  POSITION: " + str(step_output.position))
        logger.debug("  ROTATION: " + str(step_output.rotation))
        logger.debug("OBJECTS: " +
                     str(len(step_output.object_list)) +
                     " TOTAL")
        if len(step_output.object_list) > 0:
            for line in Util.generate_pretty_object_output(
                    step_output.object_list):
                logger.debug("    " + line)

    def on_end_scene(self, step_number: int, payload, controller):
        logger.info("end")
