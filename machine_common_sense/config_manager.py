import ast
import configparser  # noqa: F401
import logging
import os
from enum import Enum, unique
from typing import Dict, List, Optional, Tuple

import numpy as np
from pydantic import BaseModel as PydanticBaseModel

from .action import Action
from .goal_metadata import GoalMetadata

logger = logging.getLogger(__name__)


def to_camel_case(string: str) -> str:
    '''Converts a snake case string to camel case'''
    words = string.split('_')
    return ''.join(word.capitalize() if word !=
                   words[0] else word for word in words)


class BaseModel(PydanticBaseModel):
    # global configs are enabled by creating a custom BaseModel class
    # contain the desired config
    class Config:
        alias_generator = to_camel_case
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


@unique
class MetadataTier(Enum):
    # Normal metadata plus metadata for all hidden objects
    ORACLE = 'oracle'
    # No metadata, except for the images, depth masks, object masks,
    # and haptic/audio feedback
    LEVEL_2 = 'level2'
    # No metadata, except for the images, depth masks, and haptic/audio
    # feedback
    LEVEL_1 = 'level1'
    # No metadata, except for the images and haptic/audio
    # feedback
    NONE = 'none'
    # Default metadata level if none specified, meant for use during
    # development
    DEFAULT = 'default'


class Vector3d(BaseModel):
    x: Optional[float] = 0.0
    y: Optional[float] = 0.0
    z: Optional[float] = 0.0


class GoalObject(BaseModel):
    id: str
    image: bytes = None


class Goal(BaseModel):
    action_list: List = None  # TODO fields.Raw()
    answer: Optional[Dict]
    category: Optional[str]
    description: Optional[str]
    domains_info: Optional[Dict]
    habituation_total: Optional[int]
    info_list: Optional[List[str]]
    last_preview_phase_step: Optional[int]
    last_step: Optional[int]
    metadata: Optional[Dict]
    objects_info: Optional[Dict]
    scene_info: Optional[Dict]
    skip_preview_phase: Optional[bool]
    task_list: List[str] = None
    type_list: List[str] = None


class ActionConfig(BaseModel):
    step_begin: int
    step_end: Optional[int]
    id: str
    is_loop_animation: Optional[bool] = False


class SequenceConfig(BaseModel):
    animation: str
    end_point: Vector3d


class AgentMovementConfig(BaseModel):
    step_begin: int
    repeat: bool
    sequence: List[SequenceConfig] = []


class AgentSettings(BaseModel):
    chest: int = -1
    chest_material: int = -1
    eyes: int = -1
    feet: int = -1
    feet_material: int = -1
    glasses: int = -1
    hair: int = -1
    hair_material: int = -1
    hat_material: int = -1
    hide_hair: bool = False
    is_elder: bool = False
    jacket: int = -1
    jacket_material: int = -1
    legs: int = -1
    legs_material: int = -1
    show_beard: bool = False
    show_glasses: bool = False
    show_jacket: bool = False
    show_tie: bool = False
    skin: int = -1
    tie: int = -1
    tie_material: int = -1


class ChangeMaterialConfig(BaseModel):
    step_begin: int
    materials: List[str]


class ForceConfig(BaseModel):
    step_begin: int
    step_end: int
    vector: Vector3d = Vector3d(x=0, y=0, z=0)
    impulse: bool = False
    relative: bool = False
    repeat: bool = False
    step_wait: Optional[int]


class MoveConfig(BaseModel):
    step_begin: int
    step_end: int
    vector: Vector3d = Vector3d(x=0, y=0, z=0)
    repeat: bool = False
    step_wait: int = 0


class OpenCloseConfig(BaseModel):
    step: int
    open: bool


class PhysicsConfig(BaseModel):
    enable: bool = False
    angular_drag: float
    bounciness: float = None
    drag: float = None
    dynamic_friction: float
    static_friction: float


class LipsGapSpanConfig(BaseModel):
    low: float
    high: float


class LipGapsConfig(BaseModel):
    front: Optional[List[LipsGapSpanConfig]]
    back: Optional[List[LipsGapSpanConfig]]
    left: Optional[List[LipsGapSpanConfig]]
    right: Optional[List[LipsGapSpanConfig]]


class PlatformLipsConfig(BaseModel):
    front: bool = False
    back: bool = False
    left: bool = False
    right: bool = False
    gaps: Optional[LipGapsConfig]


class Vector2dInt(BaseModel):
    x: Optional[int]
    z: Optional[int]


class FloorPartitionConfig(BaseModel):
    left_half: Optional[float]
    right_half: Optional[float]


class FloorTexturesConfig(BaseModel):
    material: str
    positions: List[Vector2dInt] = []


class ShowConfig(BaseModel):
    step_begin: int
    position: Vector3d = Vector3d(x=0, y=0, z=0)
    rotation: Vector3d = Vector3d(x=0, y=0, z=0)
    scale: Vector3d = Vector3d(x=1, y=1, z=1)
    bounding_box: Optional[List[Dict]]  # debug property


class SizeConfig(BaseModel):
    step_begin: int
    step_end: int
    size: Vector3d = Vector3d(x=1, y=1, z=1)
    repeat: bool = False
    step_wait: int = 0


class SingleStepConfig(BaseModel):
    step_begin: int


class StepBeginEndConfig(BaseModel):
    step_begin: int
    step_end: int
    repeat: bool = False
    step_wait: int = 0


class TeleportConfig(BaseModel):
    step_begin: int
    position: Vector3d = Vector3d(x=0, y=0, z=0)


class TransformConfig(BaseModel):
    position: Vector3d = Vector3d(x=0, y=0, z=0)
    rotation: Vector3d = Vector3d(x=0, y=0, z=0)
    scale: Vector3d = Vector3d(x=1, y=1, z=1)


class RoomMaterials(BaseModel):
    front: Optional[str]
    left: Optional[str]
    right: Optional[str]
    back: Optional[str]


class PerformerStart(BaseModel):
    position: Vector3d
    rotation: Vector3d


class SceneObject(BaseModel):
    id: str
    type: str  # should this be an enum?
    actions: Optional[List[ActionConfig]]
    agent_movement: Optional[AgentMovementConfig]
    agent_settings: Optional[AgentSettings]
    associated_with_agent: Optional[str] = ""
    center_of_mass: Optional[Vector3d]
    change_materials: Optional[List[ChangeMaterialConfig]]
    debug: dict = None
    forces: List[ForceConfig] = None
    ghosts: List[StepBeginEndConfig] = None
    hides: List[SingleStepConfig] = None
    kinematic: Optional[bool]
    location_parent: Optional[str]
    locked: bool = False
    mass: Optional[float]
    materials: List[str] = None
    # deprecated; please use materials
    material_file: Optional[str]
    max_angular_velocity: Optional[float]
    # Docs say moveable's default is dependant on type.  That could
    # be a problem for the concrete classes.  Needs more review later
    moveable: Optional[bool]
    moves: List[MoveConfig] = None
    null_parent: Optional[TransformConfig]
    openable: Optional[bool]
    opened: Optional[bool]
    open_close: List[OpenCloseConfig] = None
    lips: Optional[PlatformLipsConfig]
    physics: Optional[bool]
    physics_properties: Optional[PhysicsConfig]
    pickupable: Optional[bool]
    receptacle: Optional[bool]
    reset_center_of_mass: Optional[bool]
    resizes: List[SizeConfig] = None
    rotates: List[MoveConfig] = None
    salient_materials: List[str] = None
    seesaw: Optional[bool]
    shows: List[ShowConfig] = None
    shrouds: List[StepBeginEndConfig] = None
    states: List[List[str]] = None
    structure: Optional[bool]
    teleports: List[TeleportConfig] = None
    toggle_physics: List[SingleStepConfig] = None
    torques: List[ForceConfig] = None

    # These are deprecated, but needed for Eval 3 backwards compatibility
    can_contain_target: Optional[bool]
    obstacle: Optional[bool]
    occluder: Optional[bool]
    position_y: Optional[float]
    stack_target: Optional[bool]


class ConfigManager:

    DEFAULT_ROOM_DIMENSIONS = Vector3d(x=10, y=3, z=10)
    CONFIG_FILE_ENV_VAR = 'MCS_CONFIG_FILE_PATH'
    CONFIG_DEFAULT_SECTION = 'MCS'
    CONFIG_EVALUATION_NAME = 'evaluation_name'
    CONFIG_HISTORY_ENABLED = 'history_enabled'
    CONFIG_METADATA_TIER = 'metadata'
    CONFIG_NOISE_ENABLED = 'noise_enabled'
    CONFIG_SAVE_DEBUG_IMAGES = 'save_debug_images'
    CONFIG_SAVE_DEBUG_JSON = 'save_debug_json'
    CONFIG_SIZE = 'size'
    CONFIG_TEAM = 'team'
    CONFIG_VIDEO_ENABLED = 'video_enabled'
    CONFIG_LAVA_PENALTY = 'lava_penalty'
    CONFIG_STEPS_ALLOWED_IN_LAVA = 'steps_allowed_in_lava'
    CONFIG_STEP_PENALTY = 'step_penalty'
    CONFIG_GOAL_REWARD = 'goal_reward'

    # Please keep the aspect ratio as 3:2 because the IntPhys scenes are built
    # on this assumption.
    SCREEN_WIDTH_DEFAULT = 600
    SCREEN_WIDTH_MIN = 450

    # Default steps allowed in lava before calling end scene
    STEPS_ALLOWED_IN_LAVA_DEFAULT = 0

    def __init__(self, config_file_or_dict=None):
        '''
        Configuration preferences passed in by the user.
        '''
        self._config = configparser.ConfigParser()

        # For config, look for environment variable first,
        # then look at config_file_or_dict from constructor
        try:
            if (os.getenv(self.CONFIG_FILE_ENV_VAR) is not None):
                self._read_in_config_file(os.getenv(self.CONFIG_FILE_ENV_VAR))
            elif (isinstance(config_file_or_dict, dict)):
                self._read_in_config_dict(config_file_or_dict)
            elif(isinstance(config_file_or_dict, str)):
                self._read_in_config_file(config_file_or_dict)
            else:
                raise FileNotFoundError("No config options given")
        except FileNotFoundError as err:
            raise RuntimeError("Configuration not set") from err

        self._validate_screen_size()

    def _read_in_config_dict(self, config_dict):
        self._config[self.CONFIG_DEFAULT_SECTION] = config_dict
        logger.info('No config file given or file path does not exist,'
                    ' using config dictionary')
        logger.info(f"Read in config dictionary: {str(config_dict)}")

    def _read_in_config_file(self, config_file_path):
        if os.path.exists(config_file_path):
            self._config.read(config_file_path)
            logger.info(f"Config File Path: {config_file_path}")
        else:
            logger.warning(f"No config file at given path: {config_file_path}")
            raise FileNotFoundError()

    def _validate_screen_size(self):
        if(self.get_size() < self.SCREEN_WIDTH_MIN):
            self._config.set(
                self.CONFIG_DEFAULT_SECTION,
                self.CONFIG_SIZE,
                str(self.SCREEN_WIDTH_DEFAULT)
            )

    def is_file_writing_enabled(self):
        return (
            self.is_save_debug_images() or
            self.is_save_debug_json() or
            self.is_video_enabled()
        )

    def get_evaluation_name(self):
        return self._config.get(
            self.CONFIG_DEFAULT_SECTION,
            self.CONFIG_EVALUATION_NAME,
            fallback=''
        )

    def get_metadata_tier(self):
        metadata = self._config.get(
            self.CONFIG_DEFAULT_SECTION,
            self.CONFIG_METADATA_TIER,
            fallback='default'
        )

        return MetadataTier(metadata)

    def set_metadata_tier(self, mode):
        self._config.set(
            self.CONFIG_DEFAULT_SECTION,
            self.CONFIG_METADATA_TIER,
            mode
        )

    def get_size(self):
        return self._config.getint(
            self.CONFIG_DEFAULT_SECTION,
            self.CONFIG_SIZE,
            fallback=self.SCREEN_WIDTH_DEFAULT
        )

    def get_team(self):
        return self._config.get(
            self.CONFIG_DEFAULT_SECTION,
            self.CONFIG_TEAM,
            fallback=''
        )

    def is_history_enabled(self):
        return self._config.getboolean(
            self.CONFIG_DEFAULT_SECTION,
            self.CONFIG_HISTORY_ENABLED,
            fallback=True
        )

    def is_noise_enabled(self):
        return self._config.getboolean(
            self.CONFIG_DEFAULT_SECTION,
            self.CONFIG_NOISE_ENABLED,
            fallback=False
        )

    def is_save_debug_images(self):
        return self._config.getboolean(
            self.CONFIG_DEFAULT_SECTION,
            self.CONFIG_SAVE_DEBUG_IMAGES,
            fallback=False
        )

    def is_save_debug_json(self):
        return self._config.getboolean(
            self.CONFIG_DEFAULT_SECTION,
            self.CONFIG_SAVE_DEBUG_JSON,
            fallback=False
        )

    def is_video_enabled(self):
        return self._config.getboolean(
            self.CONFIG_DEFAULT_SECTION,
            self.CONFIG_VIDEO_ENABLED,
            fallback=False
        )

    def is_depth_maps_enabled(self) -> bool:
        metadata_tier = self.get_metadata_tier()
        return metadata_tier in [
            MetadataTier.LEVEL_1,
            MetadataTier.LEVEL_2,
            MetadataTier.ORACLE,
        ]

    def is_object_masks_enabled(self) -> bool:
        metadata_tier = self.get_metadata_tier()
        return (
            metadata_tier != MetadataTier.LEVEL_1 and
            metadata_tier in
            [
                MetadataTier.LEVEL_2,
                MetadataTier.ORACLE,
            ]
        )

    def get_screen_size(self) -> Tuple[int, int]:
        return (self.get_screen_width(), self.get_screen_height())

    def get_screen_width(self) -> int:
        return self.get_size()

    def get_screen_height(self) -> int:
        size = self.get_size()
        return int(size / 3 * 2)

    def get_lava_penalty(self):
        return self._config.getfloat(
            self.CONFIG_DEFAULT_SECTION,
            self.CONFIG_LAVA_PENALTY,
            fallback=None
        )

    def get_step_penalty(self):
        return self._config.getfloat(
            self.CONFIG_DEFAULT_SECTION,
            self.CONFIG_STEP_PENALTY,
            fallback=None
        )

    def get_goal_reward(self):
        return self._config.getfloat(
            self.CONFIG_DEFAULT_SECTION,
            self.CONFIG_GOAL_REWARD,
            fallback=None
        )

    def get_steps_allowed_in_lava(self):
        return self._config.getint(
            self.CONFIG_DEFAULT_SECTION,
            self.CONFIG_STEPS_ALLOWED_IN_LAVA,
            fallback=self.STEPS_ALLOWED_IN_LAVA_DEFAULT
        )


class SceneConfiguration(BaseModel):
    '''Class for keeping track of scene configuration'''
    ceiling_material: Optional[str]
    debug: Optional[Dict]
    floor_material: Optional[str]
    floor_properties: Optional[PhysicsConfig]
    floor_textures: List[FloorTexturesConfig] = []
    goal: Optional[Goal]
    holes: List[Vector2dInt] = []
    intuitive_physics: bool = False
    isometric: bool = False
    lava: List[Vector2dInt] = []
    name: Optional[str]
    objects: List[SceneObject] = []
    observation: bool = False  # deprecated; please use intuitivePhysics
    partition_floor: Optional[FloorPartitionConfig]
    performer_start: Optional[PerformerStart]
    restrict_open_doors: Optional[bool]
    room_dimensions: Vector3d = ConfigManager.DEFAULT_ROOM_DIMENSIONS
    room_materials: Optional[RoomMaterials]
    screenshot: bool = False  # developer use only; for the image generator
    version: Optional[int]
    wall_material: Optional[str]
    wall_properties: Optional[PhysicsConfig]

    # These are deprecated, but needed for Eval 3 backwards compatibility
    evaluation: Optional[str]
    evaluation_only: Optional[bool]
    eval_name: Optional[str]
    hypercube_number: Optional[int]
    scene_number: Optional[int]
    sequence_number: Optional[int]
    training: Optional[bool]

    """
    @post_dump
    def remove_none(self, d, **kwargs) -> Dict:
        '''Remove all none's from dictionaries'''
        for key, value in dict(d).items():
            if isinstance(value, dict):
                d[key] = self.remove_none(value)
            if isinstance(value, list):
                for index, val in enumerate(value):
                    if isinstance(val, dict):
                        value[index] = self.remove_none(val)
            if value is None:
                del d[key]
        return d
    """

    def retrieve_object_states(self,
                               object_id, step_number):
        """Return the state list at the current step for the object with the
        given ID from the scene configuration data, if any."""
        state_list_each_step = next(
            (
                object_config.states or []
                for object_config in self.objects
                if object_config.id == object_id
            ),
            [],
        )

        # Retrieve the object's states in the current step.
        if len(state_list_each_step) > step_number:
            state_list = state_list_each_step[step_number]
            # Validate the data type.
            if state_list is not None:
                if not isinstance(state_list, list):
                    return [state_list]
                return [str(state) for state in state_list]
        return []

    def retrieve_goal(self, steps_allowed_in_lava=0):
        if not self.goal:
            return self.update_goal_target_image(GoalMetadata(
                steps_allowed_in_lava=steps_allowed_in_lava
            ))

        goal = self.goal

        # Transform action list data from strings to tuples.
        action_list = goal.action_list or []
        for index, action_list_at_step in enumerate(action_list):
            action_list[index] = [
                Action.input_to_action_and_params(action)
                if isinstance(action, str) else action
                for action in action_list_at_step
            ]

        if goal.category:
            # Backwards compatibility
            goal.metadata['category'] = goal.category

        return self.update_goal_target_image(
            GoalMetadata(
                action_list=action_list or None,
                category=goal.category or '',
                description=goal.description or '',
                habituation_total=goal.habituation_total or 0,
                last_preview_phase_step=(goal.last_preview_phase_step or 0),
                last_step=goal.last_step or None,
                metadata=goal.metadata or {},
                steps_allowed_in_lava=steps_allowed_in_lava
            )
        )

    def retrieve_lava(self) -> List[Tuple[float, float, float, float]]:
        """Return the list of lava locations as (X1, Z1, X2, Z2) tuples, where
        X1/Z1 is the top-left corner and X2/Z2 is the bottom-right corner."""
        lava = [
            (area.x - 0.5, area.z - 0.5, area.x + 0.5, area.z + 0.5)
            for area in self.lava
        ]
        if self.partition_floor and (
            self.partition_floor.left_half or
            self.partition_floor.right_half
        ):
            x_half = self.room_dimensions.x / 2.0
            z_half = self.room_dimensions.z / 2.0
            x_left_scale = x_half * min(self.partition_floor.left_half, 1)
            lava.append((-x_half, z_half, (-x_half + x_left_scale), -z_half))
            x_right_scale = x_half * min(self.partition_floor.right_half, 1)
            lava.append(((x_half - x_right_scale), z_half, x_half, -z_half))
        return lava

    def update_goal_target_image(self, goal_output):
        target_name_list = ['target', 'target_1', 'target_2']

        for target_name in target_name_list:
            # need to convert goal image data from string to array
            if (
                target_name in goal_output.metadata and
                'image' in goal_output.metadata[target_name] and
                isinstance(goal_output.metadata[target_name]['image'], str)
            ):
                image_list_string = goal_output.metadata[target_name]['image']
                goal_output.metadata[target_name]['image'] = np.array(
                    ast.literal_eval(image_list_string)).tolist()

        return goal_output
