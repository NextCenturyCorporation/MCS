import logging
from pathlib import Path

from .controller_events import AbstractControllerSubscriber
from .recorder import JsonRecorder
from .stringifier import Stringifier

logger = logging.getLogger(__name__)


class ControllerLogger(AbstractControllerSubscriber):
    '''Handles debugging and user output based on controller events
    '''

    def on_start_scene(self, payload):
        logger.debug(
            f"STARTING NEW SCENE: {payload.scene_config.name}")
        logger.debug(
            f"METADATA TIER: {payload.config.get_metadata_tier().value}")
        logger.debug(f"STEP: {payload.step_number}")
        logger.debug("ACTION: Initialize")

        self._write_debug_output(payload)

    def on_before_step(self, payload):
        logger.debug("================================================"
                     "===============================")
        logger.debug(f"STEP: {str(payload.step_number)}")
        logger.debug(f'ACTION: {payload.action}')
        if payload.goal.habituation_total >= payload.habituation_trial:
            logger.debug(
                f'HABITUATION TRIAL: {payload.habituation_trial} / '
                f'{payload.goal.habituation_total}'
            )

        elif payload.goal.habituation_total > 0:
            logger.debug("HABITUATION TRIAL: DONE")
        else:
            logger.debug("HABITUATION TRIAL: NONE")

    def on_after_step(self, payload):
        self._write_debug_output(payload)

    def _write_debug_output(self, payload):
        step_output = payload.restricted_step_output
        logger.debug(f"RETURN STATUS: {step_output.return_status}")
        logger.debug(f"REWARD: {str(step_output.reward)}")
        logger.debug("SELF METADATA:")
        logger.debug(f"  CAMERA HEIGHT: {str(step_output.camera_height)}")
        logger.debug(f"  HEAD TILT: {str(step_output.head_tilt)}")
        logger.debug(f"  POSITION: {str(step_output.position)}")
        logger.debug(f"  ROTATION: {str(step_output.rotation)}")
        logger.debug(f"  HAPTIC FEEDBACK: {str(step_output.haptic_feedback)}")
        logger.debug(f"OBJECTS: {len(step_output.object_list)} TOTAL")
        if len(step_output.object_list) > 0:
            for line in Stringifier.generate_pretty_object_output(
                    step_output.object_list):
                logger.debug(f"    {line}")


class ControllerDebugFileGenerator(AbstractControllerSubscriber):
    '''Handles writing mcs output debug files
    '''

    def on_start_scene(self, payload):
        self._write_debug_output_file(payload)

    def on_after_step(self, payload):
        self._write_debug_output_file(payload)

    def _write_debug_output_file(self, payload):
        step_output = \
            payload.restricted_step_output.copy_without_depth_or_images()
        if payload.output_folder and payload.config.is_save_debug_json():
            with open(
                ((f'{payload.output_folder}mcs_output_' +
                  str(payload.step_number)) + '.json'), 'w') as json_file:
                json_file.write(str(step_output))


class ControllerAi2thorFileGenerator(AbstractControllerSubscriber):
    '''Handles writing AI2Thor debug files
    '''

    def on_start_scene(self, payload):
        if payload.output_folder and payload.config.is_save_debug_json():
            path = Path(payload.output_folder) / 'ai2thor_input_{}.json'
            self._in_recorder = JsonRecorder(json_template=path)
            path = Path(payload.output_folder) / 'ai2thor_output_{}.json'
            self._out_recorder = JsonRecorder(json_template=path)
        self._write_debug_input_file(payload)
        self._write_debug_output_file(payload)

    def on_after_step(self, payload):
        self._write_debug_input_file(payload)
        self._write_debug_output_file(payload)

    def _write_debug_input_file(self, payload):
        data = payload.wrapped_step
        if self._in_recorder:
            self._in_recorder.add(data)

    def _write_debug_output_file(self, payload):
        data = {
            "metadata": payload.step_metadata.metadata
        }
        if self._out_recorder:
            self._out_recorder.add(data)
