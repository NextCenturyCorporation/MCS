import copy
import logging
from dataclasses import dataclass

import numpy as np
import PIL
from ai2thor.server import Event

from .config_manager import ConfigManager, MetadataTier, SceneConfiguration
from .controller import DEFAULT_MOVE
from .material import Material
from .object_metadata import ObjectMetadata
from .pose import Pose
from .return_status import ReturnStatus
from .reward import Reward
from .step_metadata import StepMetadata

logger = logging.getLogger(__name__)


@dataclass
class SceneEvent():
    '''Wraps step output from AI2thor'''
    _config: ConfigManager
    _scene_config: SceneConfiguration
    _raw_output: Event
    _step_number: int

    def __post_init__(self):
        max_depth = self.clipping_plane_far
        self.image_list = []
        self.depth_map_list = []
        self.object_mask_list = []

        for index, event in enumerate(self.events):
            if hasattr(event, 'frame'):
                scene_image = PIL.Image.fromarray(event.frame)
                self.image_list.append(scene_image)

                if self._config.is_depth_maps_enabled():
                    # The Unity depth array (returned by Depth.shader) contains
                    # a third of the total max depth in each RGB element.
                    unity_depth_array = event.depth_frame.astype(np.float32)
                    # Convert to values between 0 and max_depth for output.
                    depth_float_array = (
                        (unity_depth_array[:, :, 0] *
                         (max_depth / 3.0) / 255.0) +
                        (unity_depth_array[:, :, 1] *
                         (max_depth / 3.0) / 255.0) +
                        (unity_depth_array[:, :, 2] *
                         (max_depth / 3.0) / 255.0)
                    )
                    self.depth_map_list.append(np.array(depth_float_array))

                if self._config.is_object_masks_enabled():
                    object_mask = PIL.Image.fromarray(
                        event.instance_segmentation_frame)
                    self.object_mask_list.append(object_mask)

    @property
    def objects(self) -> list:
        return self._raw_output.metadata.get('objects', None)

    @property
    def agent(self) -> dict:
        return self._raw_output.metadata.get('agent', None)

    @property
    def head_tilt(self) -> float:
        return self._raw_output.metadata['agent']['cameraHorizon']

    @property
    def rotation(self) -> float:
        return self._raw_output.metadata['agent']['rotation']['y']

    @property
    def camera_field_of_view(self):
        return self._raw_output.metadata.get('fov', 0.0)

    @property
    def clipping_plane_near(self):
        return self._raw_output.metadata.get('clippingPlaneNear', 0.0)

    @property
    def clipping_plane_far(self):
        return self._raw_output.metadata.get(
            'clippingPlaneFar', ConfigManager.DEFAULT_CLIPPING_PLANE_FAR)

    @property
    def performer_radius(self):
        return self._raw_output.metadata.get('performerRadius')

    @property
    def performer_reach(self):
        return self._raw_output.metadata.get('performerReach')

    @property
    def physics_frames_per_second(self) -> float:
        return self._raw_output.metadata.get('physicsFramesPerSecond')

    @property
    def events(self):
        return self._raw_output.events

    @property
    def camera_height(self):
        return self._raw_output.metadata.get(
            'cameraPosition', {}).get('y', 0.0)

    @property
    def position(self) -> dict:
        return self._raw_output.metadata['agent']['position']

    def _get_objects(self, key: str):
        # Return object list for all tier levels, the restrict output function
        # will then strip out the necessary metadata
        metadata_tier = self._config.get_metadata_tier()
        show_all = metadata_tier != MetadataTier.DEFAULT
        # if no config specified, return visible objects (for now)
        return sorted(
            [
                self.retrieve_object_output(
                    object_metadata, self.object_colors
                )
                for object_metadata in self._raw_output.metadata[key]
                if show_all or object_metadata['visibleInCamera'] or
                object_metadata['isPickedUp']
            ],
            key=lambda x: x.uuid
        )

    @property
    def object_list(self):
        return self._get_objects('objects')

    @property
    def structural_object_list(self):
        return self._get_objects('structuralObjects')

    @property
    def return_status(self):
        return_status = ReturnStatus.UNDEFINED.name

        try:
            if self._raw_output.metadata['lastActionStatus']:
                return_status = ReturnStatus[
                    self._raw_output.metadata['lastActionStatus']
                ].name
        except KeyError:
            logger.error(
                "Return status {self._raw_output.metadata['lastActionStatus']}"
                " is not currently supported.")
        finally:
            return return_status

    @property
    def pose(self) -> str:
        pose = Pose.UNDEFINED.name

        try:
            pose = Pose[self._raw_output.metadata['pose']].name
        except KeyError:
            logger.error(
                "Pose {scene_event.metadata['pose']}"
                " is not currently supported.")
        finally:
            return pose

    @property
    def object_colors(self):
        # Use the color map for the final event (though they should all be the
        # same anyway).
        event = self._raw_output.events[len(
            self._raw_output.events) - 1]
        return event.object_id_to_color

    def retrieve_object_output(
            self, object_metadata, object_id_to_color):
        material_list = (
            list(
                filter(
                    Material.verify_material_enum_string,
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

        return ObjectMetadata(
            uuid=object_metadata['objectId'],
            dimensions=(
                bounds['objectBoundsCorners']
                if 'objectBoundsCorners' in bounds
                else None
            ),
            direction=object_metadata['direction'],
            distance=(
                object_metadata['distanceXZ'] / DEFAULT_MOVE
            ),  # DEPRECATED
            distance_in_steps=(
                object_metadata['distanceXZ'] / DEFAULT_MOVE
            ),
            distance_in_world=(object_metadata['distance']),
            held=object_metadata['isPickedUp'],
            mass=object_metadata['mass'],
            material_list=material_list,
            position=object_metadata['position'],
            rotation=object_metadata['rotation'],
            segment_color={'r': rgb[0], 'g': rgb[1], 'b': rgb[2]},
            shape=object_metadata['shape'],
            state_list=self._scene_config.retrieve_object_states(
                object_metadata['objectId'],
                self._step_number
            ),
            texture_color_list=object_metadata['colorsFromMaterials'],
            visible=(
                object_metadata['visibleInCamera'] or
                object_metadata['isPickedUp']
            ),
            is_open=object_metadata['isOpen'],
            openable=object_metadata['openable']
        )


class ControllerOutputHandler():
    '''
    Attempts to handle converting ai2thor output in to MCS output.
    This class will be refactored again in MCS-665
    '''

    def __init__(self, config: ConfigManager):
        # do nothing
        self._config = config

    def set_scene_config(self, scene_config):
        self._scene_config = scene_config

    def handle_output(self, raw_output, goal, step_number, habituation_trial):
        self._scene_event = SceneEvent(
            self._config, self._scene_config, raw_output, step_number)
        self._step_number = step_number
        unrestricted = self._get_step_metadata(
            goal, habituation_trial, False)
        restricted = self._get_step_metadata(
            goal, habituation_trial, True)
        return (unrestricted, restricted)

    # used to be wrap output
    def _get_step_metadata(self, goal, habituation_trial,
                           restricted=True) -> StepMetadata:
        metadata_tier = self._config.get_metadata_tier()
        restrict_depth_map = (
            restricted and
            metadata_tier == MetadataTier.NONE
        )

        restrict_object_mask_list = (
            restricted and
            (metadata_tier == MetadataTier.NONE or
             metadata_tier == MetadataTier.LEVEL_1)
        )

        restrict_non_oracle = (
            restricted and
            (metadata_tier == MetadataTier.NONE or
             metadata_tier == MetadataTier.LEVEL_1 or
             metadata_tier == MetadataTier.LEVEL_2)
        )

        depth_map_list = [] if restrict_depth_map else (
            self._scene_event.depth_map_list)
        image_list = self._scene_event.image_list
        object_mask_list = ([] if restrict_object_mask_list else
                            self._scene_event.object_mask_list)

        objects = self._scene_event.objects
        agent = self._scene_event.agent
        step_output = StepMetadata(
            action_list=goal.retrieve_action_list_at_step(
                self._step_number
            ),
            camera_aspect_ratio=(
                self._config.get_screen_width(),
                self._config.get_screen_height()),
            camera_clipping_planes=(
                self._scene_event.clipping_plane_near,
                self._scene_event.clipping_plane_far
            ),
            camera_field_of_view=self._scene_event.camera_field_of_view,
            camera_height=self._scene_event.camera_height,
            depth_map_list=depth_map_list,
            goal=goal,
            habituation_trial=(
                habituation_trial
                if goal.habituation_total >= habituation_trial
                else None
            ),
            head_tilt=self._scene_event.head_tilt,
            image_list=image_list,
            object_list=(
                [] if restrict_non_oracle else self._scene_event.object_list),
            object_mask_list=object_mask_list,
            pose=self._scene_event.pose,
            position=(
                None if restrict_non_oracle else self._scene_event.position),
            performer_radius=self._scene_event.performer_radius,
            performer_reach=self._scene_event.performer_reach,
            return_status=self._scene_event.return_status,
            reward=Reward.calculate_reward(
                goal, objects, agent, self._step_number,
                self._scene_event.performer_reach),
            rotation=(
                None if restrict_non_oracle else self._scene_event.rotation),
            step_number=self._step_number,
            physics_frames_per_second=(
                self._scene_event.physics_frames_per_second),
            structural_object_list=([] if restrict_non_oracle else
                                    self._scene_event.structural_object_list)
        )

        # This is here to retain the exact outputs as before
        # If None is passed into the constructor, it is turned into
        # {}, but restricted mode turns it to None.
        if (restrict_non_oracle):
            step_output.position = None

        if (restrict_non_oracle):
            target_name_list = ['target', 'target_1', 'target_2']

            for target_name in target_name_list:
                if (target_name in step_output.goal.metadata):
                    step_output.goal = copy.deepcopy(
                        step_output.goal)
                    if 'image' in step_output.goal.metadata[target_name]:
                        step_output.goal.metadata[target_name]['image'] = None
                    if 'id' in step_output.goal.metadata[target_name]:
                        step_output.goal.metadata[target_name]['id'] = None
                    if 'image_name' in step_output.goal.metadata[target_name]:
                        step_output.goal.metadata[
                            target_name]['image_name'] = None

        return step_output
