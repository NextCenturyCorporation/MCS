import logging
import json

from .controller_events import AbstractControllerSubscriber
from .util import Util

logger = logging.getLogger(__name__)


class ControllerLogger(AbstractControllerSubscriber):

    def on_start_scene(self, payload, controller):
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

    def on_before_step(self, payload, controller):
        logger.info("before step")
        logger.debug("================================================"
                     "===============================")
        logger.debug("STEP: " + str(payload.step_number))
        logger.debug("ACTION: " + payload.action)
        if payload.goal.habituation_total >= payload.habituation_trial:
            logger.debug(f"HABITUATION TRIAL: "
                         f"{str(payload.habituation_trial)}"
                         f" / {str(payload.goal.habituation_total)}")
        elif payload.goal.habituation_total > 0:
            logger.debug("HABITUATION TRIAL: DONE")
        else:
            logger.debug("HABITUATION TRIAL: NONE")

    def on_after_step(self, payload, controller):
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


class ControllerDebugFileGenerator(AbstractControllerSubscriber):

    def on_start_scene(self, payload, controller):
        self._write_debug_output_file(payload)

    def on_after_step(self, payload, controller):
        self._write_debug_output_file(payload)

    def _write_debug_output_file(self, payload):
        step_output = \
            payload.restricted_step_output.copy_without_depth_or_images()
        if payload.output_folder and payload.config.is_save_debug_json():
            with open(payload.output_folder + 'mcs_output_' +
                      str(payload.step_number) + '.json', 'w') as json_file:
                json_file.write(str(step_output))


class ControllerAi2thorFileGenerator(AbstractControllerSubscriber):

    def on_start_scene(self, payload, controller):
        self._write_debug_input_file(payload)
        self._write_debug_output_file(payload)

    def on_after_step(self, payload, controller):
        self._write_debug_input_file(payload)
        self._write_debug_output_file(payload)

    def _write_debug_input_file(self, payload):
        data = payload.wrapped_step
        name = 'ai2thor_input_'
        self._write_ai2thor_file(payload, data, name)

    def _write_debug_output_file(self, payload):
        data = {
            "metadata": payload.step_metadata.metadata
        }
        name = 'ai2thor_output_'
        self._write_ai2thor_file(payload, data, name)

    def _write_ai2thor_file(self, payload, data, name):
        if payload.output_folder and payload.config.is_save_debug_json():
            with open(payload.output_folder + name +
                      str(payload.step_number) + '.json', 'w') as json_file:
                json.dump(data, json_file, sort_keys=True, indent=4)
