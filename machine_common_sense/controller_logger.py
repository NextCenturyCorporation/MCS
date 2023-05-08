import logging
from pathlib import Path

from .config_manager import TerminalOutputMode
from .controller_events import AbstractControllerSubscriber, StartScenePayload
from .goal_metadata import GoalCategory
from .recorder import JsonRecorder
from .stringifier import Stringifier

logger = logging.getLogger(__name__)


class ControllerLogger(AbstractControllerSubscriber):
    '''Handles debugging and user output based on controller events
    '''

    def on_start_scene(self, payload):
        mode = payload.config.get_terminal_output_mode()
        if not mode:
            return

        step_output = payload.restricted_step_output

        logger.debug("=" * 79)
        logger.debug(f"STARTING NEW SCENE: {payload.scene_config.name}")
        metadata_tier = payload.config.get_metadata_tier().value
        logger.debug(f"METADATA TIER: {metadata_tier}")

        if step_output.goal and step_output.goal.category:
            logger.debug("GOAL METADATA:")
            logger.debug(f"  CATEGORY: {step_output.goal.category}")
            if step_output.goal.description:
                logger.debug(
                    f"  DESCRIPTION: {step_output.goal.description}"
                )
            if step_output.goal.last_step:
                logger.debug(f"  LAST STEP: {step_output.goal.last_step}")
            if step_output.goal.metadata:
                target_names = ['target', 'targets', 'target_1', 'target_2']
                for target_name in target_names:
                    targets = step_output.goal.metadata.get(target_name)
                    if not isinstance(targets, list):
                        targets = [targets] if targets else []
                    for i, target in enumerate(targets):
                        index = (
                            f" {i + 1} / {len(targets)}"
                            if len(targets) > 1 else ""
                        )
                        if 'id' in target:
                            logger.debug(f"  TARGET{index}: {target['id']}")
            if step_output.goal.steps_allowed_in_lava > 1:
                logger.debug(
                    f"  STEPS ALLOWED IN LAVA: "
                    f"{step_output.goal.steps_allowed_in_lava}"
                )
            if step_output.goal.triggered_by_target_sequence:
                logger.debug(
                    f"  TRIGGERED-BY-TARGET-SEQUENCE: "
                    f"{step_output.goal.triggered_by_target_sequence}"
                )

        if TerminalOutputMode.PERFORMER in mode:
            logger.debug("PERFORMER METADATA:")
            logger.debug(
                f"  CAMERA ASPECT RATIO: {step_output.camera_aspect_ratio}"
            )
            clipping_planes = step_output.camera_clipping_planes
            near_clipping_plane = round(clipping_planes[0], 4)
            far_clipping_plane = round(clipping_planes[0], 4)
            logger.debug(
                f"  CAMERA CLIPPING PLANES: "
                f"({near_clipping_plane}, {far_clipping_plane})"
            )
            logger.debug(
                f"  CAMERA FIELD OF VIEW: {step_output.camera_field_of_view}"
            )
            camera_height = round(step_output.camera_height, 4)
            logger.debug(f"  CAMERA HEIGHT: {camera_height}")
            performer_radius = round(step_output.performer_radius, 4)
            logger.debug(f"  PERFORMER RADIUS: {performer_radius}")
            logger.debug(f"  PERFORMER REACH: {step_output.performer_reach}")
            logger.debug(
                f"  PHYSICS FRAMES PER SECOND: "
                f"{step_output.physics_frames_per_second}"
            )

        if TerminalOutputMode.SCENE in mode:
            logger.debug("SCENE METADATA:")
            show_none = True
            if step_output.holes:
                logger.debug(f"  HOLES: {step_output.holes}")
                show_none = False
            if step_output.lava:
                logger.debug(f"  LAVA: {step_output.lava}")
                show_none = False
            if step_output.room_dimensions is not None:
                logger.debug(
                    f"  ROOM DIMENSIONS: {step_output.room_dimensions}"
                )
                show_none = False
            if show_none:
                logger.debug("  NONE")

        self.on_before_step(payload)
        self._write_debug_output(payload)

    def on_before_step(self, payload):
        mode = payload.config.get_terminal_output_mode()
        if not mode:
            return

        if isinstance(payload, StartScenePayload):
            payload = payload.restricted_step_output

        logger.debug("-" * 79)
        logger.debug(f"STEP: {payload.step_number}")
        if payload.step_number == 0:
            logger.debug("ACTION: Initialize")
        else:
            logger.debug(f'ACTION: {payload.action}')

        if payload.habituation_trial is not None and payload.goal:
            if payload.goal.habituation_total >= payload.habituation_trial:
                logger.debug(
                    f'HABITUATION TRIAL: {payload.habituation_trial} / '
                    f'{payload.goal.habituation_total}'
                )
            elif payload.goal.habituation_total > 0:
                logger.debug("HABITUATION TRIAL: DONE")

    def on_after_step(self, payload):
        mode = payload.config.get_terminal_output_mode()
        if not mode:
            return

        self._write_debug_output(payload)

    def _write_debug_output(self, payload):
        mode = payload.config.get_terminal_output_mode()
        if not mode:
            return

        step_output = payload.restricted_step_output
        if payload.step_number > 0:
            if step_output.resolved_object:
                logger.debug(f"RESOLVED OBJECT: {step_output.resolved_object}")
            if step_output.resolved_receptacle:
                logger.debug(
                    f"RESOLVED RECEPTACLE: {step_output.resolved_receptacle}"
                )
            logger.debug(f"RETURN STATUS: {step_output.return_status}")
            if step_output.goal and step_output.goal.category in [
                GoalCategory.IMITATION.value,
                GoalCategory.MULTI_RETRIEVAL.value,
                GoalCategory.RETRIEVAL.value
            ]:
                logger.debug(f"REWARD: {step_output.reward}")
            if step_output.triggered_by_sequence_incorrect:
                logger.debug("TRIGGERED-BY-SEQUENCE INCORRECT")

        if TerminalOutputMode.PERFORMER in mode:
            logger.debug("PERFORMER METADATA:")
            haptic_feedback = step_output.haptic_feedback
            logger.debug(f"  HAPTIC FEEDBACK: {haptic_feedback}")
            logger.debug(f"  HEAD TILT: {round(step_output.head_tilt, 4)}")
            if step_output.position is not None:
                position = Stringifier.vector_to_string(step_output.position)
                logger.debug(f"  POSITION: {position}")
            if step_output.rotation is not None:
                logger.debug(f"  ROTATION: {round(step_output.rotation, 4)}")

        objects = step_output.object_list
        if TerminalOutputMode.OBJECTS in mode and objects:
            logger.debug(f"OBJECTS: ({len(objects)} TOTAL)")
            lines = Stringifier.generate_pretty_object_output(objects)
            for line in lines:
                logger.debug(f"    {line}")

        structural_objects = step_output.structural_object_list
        if TerminalOutputMode.SCENE in mode and structural_objects:
            logger.debug(
                f"STRUCTURAL OBJECTS: ({len(structural_objects)} TOTAL)"
            )
            lines = Stringifier.generate_pretty_object_output(
                structural_objects
            )
            for line in lines:
                logger.debug(f"    {line}")

        if TerminalOutputMode.ACTIONS in mode and step_output.action_list:
            logger.debug("AVAILABLE ACTIONS:")
            for action, params in step_output.action_list:
                params = ",".join([f"{k}={v}" for k, v in params.items()])
                logger.debug(f"  {action}{',' if params else ''}{params}")


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
