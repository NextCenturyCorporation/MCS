import logging
import copy
import PIL
import numpy as np

from .controller import DEFAULT_MOVE
from .reward import Reward
from .step_metadata import StepMetadata
from .pose import Pose
from .return_status import ReturnStatus
from .object_metadata import ObjectMetadata
from .util import Util
from .config_manager import ConfigManager, SceneConfiguration


# from .reward import Reward
# from .step_metadata import StepMetadata

logger = logging.getLogger(__name__)


class ControllerOutputHandler():

    def __init__(self, config: ConfigManager):
        # do nothing
        self._config = config

    def set_scene_config(self, scene_config):
        self._scene_config = scene_config

    def handle_output(self, raw_output, goal, step_number, habituation_trial):
        # output_copy = copy.deepcopy(raw_output)
        # pre_restrict_output = self.wrap_output(
        #    output_copy, goal, step_number, habituation_trial)
        # output = self.restrict_step_output_metadata(pre_restrict_output)
        # return (pre_restrict_output, output)

        step_output = StepOutput(
            self._config,
            self._scene_config,
            raw_output,
            step_number)
        unrestricted = step_output.get_step_metadata(
            goal, habituation_trial, False)
        restricted = step_output.get_step_metadata(
            goal, habituation_trial, True)
        return (unrestricted, restricted)

    def restrict_step_output_metadata(self, step_output):
        # Use this function to filter out of the step output any data
        # that shouldn't be returned at certain metadata tiers
        metadata_tier = self._config.get_metadata_tier()
        if(metadata_tier == ConfigManager.CONFIG_METADATA_TIER_NONE):
            step_output.depth_map_list = []

        if(metadata_tier == ConfigManager.CONFIG_METADATA_TIER_NONE or
                metadata_tier == ConfigManager.CONFIG_METADATA_TIER_LEVEL_1):
            step_output.object_mask_list = []

        if (
            metadata_tier == ConfigManager.CONFIG_METADATA_TIER_NONE or
            metadata_tier == ConfigManager.CONFIG_METADATA_TIER_LEVEL_1 or
            metadata_tier == ConfigManager.CONFIG_METADATA_TIER_LEVEL_2
        ):
            step_output.position = None
            step_output.rotation = None
            step_output.structural_object_list = []
            step_output.object_list = []

            # Below is to remove the goal targets from output
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


class StepOutput:

    def __init__(self, config: ConfigManager, scene_config,
                 raw_output: dict, step_number: int):
        self._config = config
        self._raw_output = copy.deepcopy(raw_output)
        self._step_number = step_number
        self._scene_config = scene_config

        self._image_list, self._depth_map_list, self._object_mask_list = \
            self.save_image_data(
                self._raw_output.metadata.get(
                    'clippingPlaneFar',
                    ConfigManager.DEFAULT_CLIPPING_PLANE_FAR
                )
            )

    # used to be wrap output
    def get_step_metadata(self, goal, habituation_trial, restricted=True):
        metadata_tier = self._config.get_metadata_tier()
        restrict_depth_map = (
            restricted and
            metadata_tier == ConfigManager.CONFIG_METADATA_TIER_NONE
        )

        restrict_object_mask_list = (
            restricted and
            (metadata_tier == ConfigManager.CONFIG_METADATA_TIER_NONE or
             metadata_tier == ConfigManager.CONFIG_METADATA_TIER_LEVEL_1)
        )

        restrict_non_oracle = (
            restricted and
            (metadata_tier == ConfigManager.CONFIG_METADATA_TIER_NONE or
             metadata_tier == ConfigManager.CONFIG_METADATA_TIER_LEVEL_1 or
             metadata_tier == ConfigManager.CONFIG_METADATA_TIER_LEVEL_2)
        )

        depth_map_list = [] if restrict_depth_map else self._depth_map_list
        image_list = [] if restrict_non_oracle else self._image_list
        object_mask_list = ([] if restrict_object_mask_list else
                            self._object_mask_list)

        objects = self._raw_output.metadata.get('objects', None)
        agent = self._raw_output.metadata.get('agent', None)
        step_output = StepMetadata(
            action_list=goal.retrieve_action_list_at_step(
                self._step_number
            ),
            camera_aspect_ratio=(
                self._config.get_screen_width(),
                self._config.get_screen_height()),
            camera_clipping_planes=(
                self._raw_output.metadata.get('clippingPlaneNear', 0.0),
                self._raw_output.metadata.get('clippingPlaneFar', 0.0),
            ),
            camera_field_of_view=self._raw_output.metadata.get('fov', 0.0),
            camera_height=self._raw_output.metadata.get(
                'cameraPosition', {}).get('y', 0.0),
            depth_map_list=depth_map_list,
            goal=goal,
            habituation_trial=(
                habituation_trial
                if goal.habituation_total >= habituation_trial
                else None
            ),
            head_tilt=self.retrieve_head_tilt(),
            image_list=image_list,
            object_list=(
                [] if restrict_non_oracle else self.retrieve_object_list()),
            object_mask_list=object_mask_list,
            pose=self.retrieve_pose(),
            position=(
                None if restrict_non_oracle else self.retrieve_position()),
            performer_radius=self._raw_output.metadata.get('performerRadius'),
            performer_reach=self._raw_output.metadata.get('performerReach'),
            return_status=self.retrieve_return_status(),
            reward=Reward.calculate_reward(
                goal, objects, agent, self._step_number,
                self._raw_output.metadata.get('performerReach')),
            rotation=(
                None if restrict_non_oracle else self.retrieve_rotation()),
            step_number=self._step_number,
            physics_frames_per_second=self._raw_output.metadata.get(
                'physicsFramesPerSecond'),
            structural_object_list=([] if restrict_non_oracle else
                                    self.retrieve_structural_object_list())
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
        # not needed?  delete if this makes it to the code review
        # self.__head_tilt = step_output.head_tilt

        return step_output

    def retrieve_head_tilt(self):
        return self._raw_output.metadata['agent']['cameraHorizon']

    def retrieve_rotation(self):
        return self._raw_output.metadata['agent']['rotation']['y']

    def retrieve_position(self) -> dict:
        return self._raw_output.metadata['agent']['position']

    def retrieve_pose(self) -> str:
        pose = Pose.UNDEFINED.name

        try:
            pose = Pose[self._raw_output.metadata['pose']].name
        except KeyError:
            logger.error(
                "Pose {scene_event.metadata['pose']}"
                " is not currently supported.")
        finally:
            return pose

    def retrieve_object_colors(self):
        # Use the color map for the final event (though they should all be the
        # same anyway).
        return self._raw_output.events[len(
            self._raw_output.events) - 1].object_id_to_color

    # TODO need to fix
    def retrieve_object_list(self):
        # Return object list for all tier levels, the restrict output function
        # will then strip out the necessary metadata
        metadata_tier = self._config.get_metadata_tier()
        if (metadata_tier != ConfigManager.CONFIG_METADATA_TIER_DEFAULT):
            return sorted(
                [
                    self.retrieve_object_output(
                        object_metadata,
                        self.retrieve_object_colors()
                    )
                    for object_metadata in self._raw_output.metadata['objects']
                ],
                key=lambda x: x.uuid
            )
        else:
            # if no config specified, return visible objects (for now)
            return sorted(
                [
                    self.retrieve_object_output(
                        object_metadata,
                        self.retrieve_object_colors(self._raw_output)
                    )
                    for object_metadata in self._raw_output.metadata['objects']
                    if object_metadata['visibleInCamera'] or
                    object_metadata['isPickedUp']
                ],
                key=lambda x: x.uuid
            )

    def retrieve_return_status(self):
        # TODO MCS-47 Need to implement all proper step statuses on the Unity
        # side
        return_status = ReturnStatus.UNDEFINED.name

        try:
            if self._raw_output.metadata['lastActionStatus']:
                return_status = ReturnStatus[
                    self._raw_output.metadata['lastActionStatus']
                ].name
        except KeyError:
            logger.error(
                "Return status {scene_event.metadata['lastActionStatus']}"
                " is not currently supported.")
        finally:
            return return_status

    def retrieve_structural_object_list(self):
        # Return structural object list for all tier levels, the restrict
        # output function will then strip out the necessary metadata
        metadata_tier = self._config.get_metadata_tier()
        if (metadata_tier != ConfigManager().CONFIG_METADATA_TIER_DEFAULT):
            return sorted(
                [
                    self.retrieve_object_output(
                        object_metadata,
                        self.retrieve_object_colors()
                    )
                    for object_metadata in self._raw_output.metadata[
                        'structuralObjects'
                    ]
                ],
                key=lambda x: x.uuid
            )
        else:
            # if no config specified, return visible structural objects (for
            # now)
            return sorted(
                [
                    self.retrieve_object_output(
                        object_metadata, self.retrieve_object_colors()
                    )
                    for object_metadata in self._raw_output.metadata[
                        'structuralObjects'
                    ]
                    if object_metadata['visibleInCamera']
                ],
                key=lambda x: x.uuid
            )

    def retrieve_object_output(
            self, object_metadata, object_id_to_color):
        material_list = (
            list(
                filter(
                    Util.verify_material_enum_string,
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
            color={'r': rgb[0], 'g': rgb[1], 'b': rgb[2]},
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
            shape=object_metadata['shape'],
            state_list=SceneConfiguration.retrieve_object_states(
                self._scene_config, object_metadata['objectId'],
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

    def save_image_data(self, max_depth):
        image_list = []
        depth_map_list = []
        object_mask_list = []

        for index, event in enumerate(self._raw_output.events):
            scene_image = PIL.Image.fromarray(event.frame)
            image_list.append(scene_image)

            if self._config.is_depth_maps_enabled():
                # The Unity depth array (returned by Depth.shader) contains
                # a third of the total max depth in each RGB element.
                unity_depth_array = event.depth_frame.astype(np.float32)
                # Convert to values between 0 and max_depth for output.
                depth_float_array = (
                    (unity_depth_array[:, :, 0] * (max_depth / 3.0) / 255.0) +
                    (unity_depth_array[:, :, 1] * (max_depth / 3.0) / 255.0) +
                    (unity_depth_array[:, :, 2] * (max_depth / 3.0) / 255.0)
                )
                depth_map_list.append(np.array(depth_float_array))

            if self._config.is_object_masks_enabled():
                object_mask = PIL.Image.fromarray(
                    event.instance_segmentation_frame)
                object_mask_list.append(object_mask)

        return image_list, depth_map_list, object_mask_list
