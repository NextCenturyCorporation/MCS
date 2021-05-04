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

    def handle_output(self, step_output, goal, step_number, habituation_trial):
        output_copy = copy.deepcopy(step_output)
        pre_restrict_output = self.wrap_output(
            output_copy, goal, step_number, habituation_trial)
        output = self.restrict_step_output_metadata(pre_restrict_output)
        return (pre_restrict_output, output)

    def wrap_output(self, scene_event, goal, step_number, habituation_trial):
        image_list, depth_map_list, object_mask_list = self.save_image_data(
            scene_event,
            scene_event.metadata.get(
                'clippingPlaneFar',
                ConfigManager.DEFAULT_CLIPPING_PLANE_FAR
            )
        )

        objects = scene_event.metadata.get('objects', None)
        agent = scene_event.metadata.get('agent', None)
        step_output = StepMetadata(
            action_list=goal.retrieve_action_list_at_step(
                step_number
            ),
            camera_aspect_ratio=(
                self._config.get_screen_width(),
                self._config.get_screen_height()),
            camera_clipping_planes=(
                scene_event.metadata.get('clippingPlaneNear', 0.0),
                scene_event.metadata.get('clippingPlaneFar', 0.0),
            ),
            camera_field_of_view=scene_event.metadata.get('fov', 0.0),
            camera_height=scene_event.metadata.get(
                'cameraPosition', {}).get('y', 0.0),
            depth_map_list=depth_map_list,
            goal=goal,
            habituation_trial=(
                habituation_trial
                if goal.habituation_total >= habituation_trial
                else None
            ),
            head_tilt=self.retrieve_head_tilt(scene_event),
            image_list=image_list,
            object_list=self.retrieve_object_list(scene_event, step_number),
            object_mask_list=object_mask_list,
            pose=self.retrieve_pose(scene_event),
            position=self.retrieve_position(scene_event),
            performer_radius=scene_event.metadata.get('performerRadius'),
            performer_reach=scene_event.metadata.get('performerReach'),
            return_status=self.retrieve_return_status(scene_event),
            reward=Reward.calculate_reward(
                goal, objects, agent, step_number,
                scene_event.metadata.get('performerReach')),
            rotation=self.retrieve_rotation(scene_event),
            step_number=step_number,
            physics_frames_per_second=scene_event.metadata.get(
                'physicsFramesPerSecond'),
            structural_object_list=self.retrieve_structural_object_list(
                scene_event, step_number)
        )

        # not needed?  delete if this makes it to the code review
        # self.__head_tilt = step_output.head_tilt

        return step_output

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
                    if 'image' in step_output.goal.metadata[target_name]:
                        step_output.goal.metadata[target_name]['image'] = None
                    if 'id' in step_output.goal.metadata[target_name]:
                        step_output.goal.metadata[target_name]['id'] = None
                    if 'image_name' in step_output.goal.metadata[target_name]:
                        step_output.goal.metadata[
                            target_name]['image_name'] = None

        return step_output

    def save_image_data(self, scene_event, max_depth):
        image_list = []
        depth_map_list = []
        object_mask_list = []

        for index, event in enumerate(scene_event.events):
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

    # TODO need to fix
    def retrieve_object_list(self, scene_event, step_number):
        # Return object list for all tier levels, the restrict output function
        # will then strip out the necessary metadata
        metadata_tier = self._config.get_metadata_tier()
        if (metadata_tier != ConfigManager.CONFIG_METADATA_TIER_DEFAULT):
            return sorted(
                [
                    self.retrieve_object_output(
                        object_metadata,
                        self.retrieve_object_colors(scene_event),
                        step_number
                    )
                    for object_metadata in scene_event.metadata['objects']
                ],
                key=lambda x: x.uuid
            )
        else:
            # if no config specified, return visible objects (for now)
            return sorted(
                [
                    self.retrieve_object_output(
                        object_metadata,
                        self.retrieve_object_colors(scene_event)
                    )
                    for object_metadata in scene_event.metadata['objects']
                    if object_metadata['visibleInCamera'] or
                    object_metadata['isPickedUp']
                ],
                key=lambda x: x.uuid
            )

    def retrieve_head_tilt(self, scene_event):
        return scene_event.metadata['agent']['cameraHorizon']

    def retrieve_rotation(self, scene_event):
        return scene_event.metadata['agent']['rotation']['y']

    def retrieve_position(self, scene_event) -> dict:
        return scene_event.metadata['agent']['position']

    def retrieve_pose(self, scene_event) -> str:
        pose = Pose.UNDEFINED.name

        try:
            pose = Pose[scene_event.metadata['pose']].name
        except KeyError:
            logger.error(
                "Pose {scene_event.metadata['pose']}"
                " is not currently supported.")
        finally:
            return pose

    def retrieve_return_status(self, scene_event):
        # TODO MCS-47 Need to implement all proper step statuses on the Unity
        # side
        return_status = ReturnStatus.UNDEFINED.name

        try:
            if scene_event.metadata['lastActionStatus']:
                return_status = ReturnStatus[
                    scene_event.metadata['lastActionStatus']
                ].name
        except KeyError:
            logger.error(
                "Return status {scene_event.metadata['lastActionStatus']}"
                " is not currently supported.")
        finally:
            return return_status

    def retrieve_structural_object_list(self, scene_event, step_number):
        # Return structural object list for all tier levels, the restrict
        # output function will then strip out the necessary metadata
        metadata_tier = self._config.get_metadata_tier()
        if (metadata_tier != ConfigManager().CONFIG_METADATA_TIER_DEFAULT):
            return sorted(
                [
                    self.retrieve_object_output(
                        object_metadata,
                        self.retrieve_object_colors(scene_event),
                        step_number
                    )
                    for object_metadata in scene_event.metadata[
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
                        object_metadata, self.retrieve_object_colors(
                            scene_event, step_number)
                    )
                    for object_metadata in scene_event.metadata[
                        'structuralObjects'
                    ]
                    if object_metadata['visibleInCamera']
                ],
                key=lambda x: x.uuid
            )

    def retrieve_object_output(
            self, object_metadata, object_id_to_color, step_number):
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
                self._scene_config, object_metadata['objectId'], step_number
            ),
            texture_color_list=object_metadata['colorsFromMaterials'],
            visible=(
                object_metadata['visibleInCamera'] or
                object_metadata['isPickedUp']
            ),
            is_open=object_metadata['isOpen'],
            openable=object_metadata['openable']
        )

    def retrieve_object_colors(self, scene_event):
        # Use the color map for the final event (though they should all be the
        # same anyway).
        return scene_event.events[len(
            scene_event.events) - 1].object_id_to_color
