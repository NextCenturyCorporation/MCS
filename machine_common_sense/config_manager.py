import ast
import configparser  # noqa: F401
import logging
import os
from dataclasses import dataclass, field
from enum import Enum, unique
from typing import Dict, List, Tuple

import numpy as np
from marshmallow import Schema, fields, post_load
from marshmallow.decorators import post_dump

from .action import Action
from .goal_metadata import GoalMetadata

logger = logging.getLogger(__name__)


@dataclass
class Vector3d:
    # There is probably a class like this in python somewhere
    # but i don't know where it is.
    # TODO change later, potentially rename?
    x: float = 0
    y: float = 0
    z: float = 0


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


class ConfigManager(object):

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


class Vector3dSchema(Schema):
    x = fields.Float()
    y = fields.Float()
    z = fields.Float()

    @post_load
    def make_position_3d(self, data, **kwargs):
        return Vector3d(**data)


class RoomMaterialsSchema(Schema):
    front = fields.Str()
    left = fields.Str()
    right = fields.Str()
    back = fields.Str()

    @post_load
    def make_room_materials(self, data, **kwargs):
        return RoomMaterials(**data)


class PerformerStartSchema(Schema):
    position = fields.Nested(Vector3dSchema)
    rotation = fields.Nested(Vector3dSchema)

    @post_load
    def make_performer_start(self, data, **kwargs):
        return PerformerStart(**data)


class GoalObjectSchema(Schema):
    id = fields.Str()
    image = fields.Raw(allow_none=True)


class GoalMetadataSchema(Schema):
    choose = fields.List(fields.Str())
    target = fields.Nested(GoalObjectSchema)
    target_1 = fields.Nested(GoalObjectSchema)
    target_2 = fields.Nested(GoalObjectSchema)


class GoalSchema(Schema):
    action_list = fields.List(fields.Raw())
    answer = fields.Dict()  # UI property
    category = fields.Str()
    description = fields.Str()
    domains_info = fields.Dict(data_key='domainsInfo')  # UI property
    habituation_total = fields.Int()
    info_list = fields.List(fields.Str())
    last_preview_phase_step = fields.Int()
    last_step = fields.Int()
    metadata = fields.Dict()
    objects_info = fields.Dict(data_key='objectsInfo')  # UI property
    scene_info = fields.Dict(data_key='sceneInfo')  # UI property
    skip_preview_phase = fields.Bool()
    task_list = fields.List(fields.Str())
    type_list = fields.List(fields.Str())

    @post_load
    def make_goal(self, data, **kwargs):
        return Goal(**data)


class ChangeMaterialConfigSchema(Schema):
    step_begin = fields.Int(data_key='stepBegin')
    materials = fields.List(fields.Str())

    @post_load
    def make_change_material(self, data, **kwargs):
        return ChangeMaterialConfig(**data)


class ForceConfigSchema(Schema):
    step_begin = fields.Int(data_key='stepBegin')
    step_end = fields.Int(data_key='stepEnd')
    vector = fields.Nested(Vector3dSchema)
    impulse = fields.Bool()
    relative = fields.Bool()
    repeat = fields.Bool()
    step_wait = fields.Int(data_key='stepWait')

    @post_load
    def make_force_config(self, data, **kwargs):
        return ForceConfig(**data)


class MoveConfigSchema(Schema):
    step_begin = fields.Int(data_key='stepBegin')
    step_end = fields.Int(data_key='stepEnd')
    vector = fields.Nested(Vector3dSchema)
    repeat = fields.Bool()
    step_wait = fields.Int(data_key='stepWait')

    @post_load
    def make_move_config(self, data, **kwargs):
        return MoveConfig(**data)


class OpenCloseConfigSchema(Schema):
    step = fields.Int()
    open = fields.Bool()

    @post_load
    def make_move_config(self, data, **kwargs):
        return OpenCloseConfig(**data)


class PhysicsConfigSchema(Schema):
    enable = fields.Bool()
    angular_drag = fields.Float(data_key='angularDrag')
    bounciness = fields.Float()
    drag = fields.Float()
    dynamic_friction = fields.Float(data_key='dynamicFriction')
    static_friction = fields.Float(data_key='staticFriction')

    @post_load
    def make_physics_config(self, data, **kwargs):
        return PhysicsConfig(**data)


class LipsGapSpanConfigSchema(Schema):
    low = fields.Float()
    high = fields.Float()

    @post_load
    def make_lip_gaps_config(self, data, **kwargs):
        return LipsGapSpanConfig(**data)


class LipsGapsConfigSchema(Schema):
    front = fields.List(fields.Nested(LipsGapSpanConfigSchema))
    back = fields.List(fields.Nested(LipsGapSpanConfigSchema))
    left = fields.List(fields.Nested(LipsGapSpanConfigSchema))
    right = fields.List(fields.Nested(LipsGapSpanConfigSchema))

    @post_load
    def make_lip_gaps_config(self, data, **kwargs):
        return LipGapsConfig(**data)


class PlatformLipsConfigSchema(Schema):
    front = fields.Bool()
    back = fields.Bool()
    left = fields.Bool()
    right = fields.Bool()
    gaps = fields.Nested(LipsGapsConfigSchema)

    @post_load
    def make_platform_lips_config(self, data, **kwargs):
        return PlatformLipsConfig(**data)


class Vector2dIntSchema(Schema):
    x = fields.Int()
    z = fields.Int()

    @post_load
    def make_holes_config(self, data, **kwargs):
        return Vector2dInt(**data)


class FloorTexturesConfigSchema(Schema):
    material = fields.Str()
    positions = fields.List(fields.Nested(Vector2dIntSchema))

    @post_load
    def make_floor_textures_config(self, data, **kwargs):
        return FloorTexturesConfig(**data)


class ShowConfigSchema(Schema):
    step_begin = fields.Int(data_key='stepBegin')
    position = fields.Nested(Vector3dSchema)
    rotation = fields.Nested(Vector3dSchema)
    scale = fields.Nested(Vector3dSchema)
    bounding_box = fields.List(fields.Dict(),
                               data_key='boundingBox')  # debug property

    @post_load
    def make_show_config(self, data, **kwargs):
        return ShowConfig(**data)


class SizeConfigSchema(Schema):
    step_begin = fields.Int(data_key='stepBegin')
    step_end = fields.Int(data_key='stepEnd')
    size = fields.Nested(Vector3dSchema)
    repeat = fields.Bool()
    step_wait = fields.Int(data_key='stepWait')

    @post_load
    def make_size_config(self, data, **kwargs):
        return SizeConfig(**data)


class SingleStepConfigSchema(Schema):
    step_begin = fields.Int(data_key='stepBegin')

    @post_load
    def make_single_step_config(self, data, **kwargs):
        return SingleStepConfig(**data)


class StepBeginEndConfigSchema(Schema):
    step_begin = fields.Int(data_key='stepBegin')
    step_end = fields.Int(data_key='stepEnd')
    repeat = fields.Bool()
    step_wait = fields.Int(data_key='stepWait')

    @post_load
    def make_step_begin_end_config(self, data, **kwargs):
        return StepBeginEndConfig(**data)


class TeleportConfigSchema(Schema):
    step_begin = fields.Int(data_key='stepBegin')
    position = fields.Nested(Vector3dSchema)

    @post_load
    def make_teleport_config(self, data, **kwargs):
        return TeleportConfig(**data)


class TransformConfigSchema(Schema):
    position = fields.Nested(Vector3dSchema)
    rotation = fields.Nested(Vector3dSchema)
    scale = fields.Nested(Vector3dSchema)

    @post_load
    def make_transform_config(self, data, **kwargs):
        return TransformConfig(**data)


class SceneObjectSchema(Schema):
    id = fields.Str()
    type = fields.Str()  # should this be an enum?
    center_of_mass = fields.Nested(Vector3dSchema, data_key='centerOfMass')
    change_materials = fields.List(
        fields.Nested(ChangeMaterialConfigSchema),
        data_key='changeMaterials')
    debug = fields.Dict()
    forces = fields.List(fields.Nested(ForceConfigSchema))
    ghosts = fields.List(fields.Nested(StepBeginEndConfigSchema))
    hides = fields.List(fields.Nested(SingleStepConfigSchema))
    kinematic = fields.Bool()
    location_parent = fields.Str(data_key='locationParent')
    locked = fields.Bool()
    mass = fields.Float()
    materials = fields.List(fields.Str())
    # deprecated; please use materials
    material_file = fields.Str(data_key='materialFile')
    max_angular_velocity = fields.Float(data_key='maxAngularVelocity')
    moveable = fields.Bool()
    moves = fields.List(fields.Nested(MoveConfigSchema))
    null_parent = fields.Nested(TransformConfigSchema, data_key='nullParent')
    openable = fields.Bool()
    opened = fields.Bool()
    open_close = fields.List(
        fields.Nested(OpenCloseConfigSchema),
        data_key='openClose')
    physics = fields.Bool()
    physics_properties = fields.Nested(
        PhysicsConfigSchema,
        data_key='physicsProperties')
    pickupable = fields.Bool()
    lips = fields.Nested(
        PlatformLipsConfigSchema, data_key='lips')
    receptacle = fields.Bool()
    reset_center_of_mass = fields.Bool(data_key='resetCenterOfMass')
    resizes = fields.List(fields.Nested(SizeConfigSchema))
    rotates = fields.List(fields.Nested(MoveConfigSchema))
    salient_materials = fields.List(fields.Str(), data_key='salientMaterials')
    seesaw = fields.Bool()
    shows = fields.List(fields.Nested(ShowConfigSchema))
    shrouds = fields.List(fields.Nested(StepBeginEndConfigSchema))
    states = fields.List(fields.List(fields.Str(), allow_none=True))
    structure = fields.Bool()
    teleports = fields.List(fields.Nested(TeleportConfigSchema))
    toggle_physics = fields.List(
        fields.Nested(SingleStepConfigSchema),
        data_key='togglePhysics')
    torques = fields.List(fields.Nested(ForceConfigSchema))

    # These are deprecated, but needed for Eval 3 backwards compatibility
    can_contain_target = fields.Bool(data_key='canContainTarget')
    obstacle = fields.Bool()
    occluder = fields.Bool()
    position_y = fields.Float(data_key='positionY')
    stack_target = fields.Bool(data_key='stackTarget')

    @post_load
    def make_scene_object(self, data, **kwargs):
        return SceneObject(**data)


class SceneConfigurationSchema(Schema):
    # The passive agent scenes can have a None ceilingMaterial
    ceiling_material = fields.Str(allow_none=True, data_key='ceilingMaterial')
    debug = fields.Dict()
    floor_material = fields.Str(data_key='floorMaterial')
    floor_properties = fields.Nested(
        PhysicsConfigSchema,
        data_key='floorProperties')
    floor_textures = fields.List(
        fields.Nested(FloorTexturesConfigSchema),
        data_key='floorTextures')
    goal = fields.Nested(GoalSchema)
    holes = fields.List(fields.Nested(Vector2dIntSchema))
    intuitive_physics = fields.Bool(data_key='intuitivePhysics')
    isometric = fields.Bool()
    lava = fields.List(fields.Nested(Vector2dIntSchema))
    name = fields.Str()
    objects = fields.List(fields.Nested(SceneObjectSchema))
    observation = fields.Bool()  # deprecated; please use intuitivePhysics
    performer_start = fields.Nested(
        PerformerStartSchema,
        data_key='performerStart')
    restrict_open_doors = fields.Bool(data_key='restrictOpenDoors')
    room_dimensions = fields.Nested(Vector3dSchema, data_key='roomDimensions')
    room_materials = fields.Nested(
        RoomMaterialsSchema,
        data_key='roomMaterials')
    screenshot = fields.Bool()  # developer use only; for the image generator
    version = fields.Integer()
    wall_material = fields.Str(data_key='wallMaterial')
    wall_properties = fields.Nested(
        PhysicsConfigSchema,
        data_key='wallProperties')

    # These are deprecated, but needed for Eval 3 backwards compatibility
    evaluation = fields.Str(allow_none=True)
    evaluation_only = fields.Bool(data_key='evaluationOnly')
    eval_name = fields.Str(data_key='evalName')
    hypercube_number = fields.Int(data_key='hypercubeNumber')
    scene_number = fields.Int(data_key='sceneNumber')
    sequence_number = fields.Int(data_key='sequenceNumber')
    training = fields.Bool()

    @post_load
    def make_scene_configuration(self, data, **kwargs):
        return SceneConfiguration(**data)

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


@dataclass
class RoomMaterials:
    front: str = None
    left: str = None
    right: str = None
    back: str = None


@dataclass
class PerformerStart:
    position: Vector3d
    rotation: Vector3d


@dataclass
class Goal:
    action_list: list = None
    answer: dict = None  # UI property
    category: str = None
    description: str = None
    domains_info: dict = None  # UI property
    habituation_total: int = None
    info_list: list = None
    last_preview_phase_step: int = None
    last_step: int = None
    # TODO metadata objects
    metadata: dict = None
    objects_info: dict = None  # UI property
    scene_info: dict = None  # UI property
    skip_preview_phase: bool = False
    task_list: List[str] = None
    type_list: List[str] = None


@dataclass
class ChangeMaterialConfig:
    step_begin: int
    materials: List[str]


@dataclass
class ForceConfig:
    step_begin: int
    step_end: int
    vector: Vector3d = Vector3d(0, 0, 0)
    impulse: bool = False
    relative: bool = False
    repeat: bool = False
    step_wait: int = 0


@dataclass
class MoveConfig:
    step_begin: int
    step_end: int
    vector: Vector3d = Vector3d(0, 0, 0)
    repeat: bool = False
    step_wait: int = 0


@dataclass
class OpenCloseConfig:
    step: int
    open: bool


@dataclass
class PhysicsConfig:
    enable: bool = False
    angular_drag: float = None
    bounciness: float = None
    drag: float = None
    dynamic_friction: float = None
    static_friction: float = None


@dataclass
class Vector2dInt:
    x: int = None
    z: int = None


@dataclass
class LipsGapSpanConfig:
    low: float = None
    high: float = None


@dataclass
class LipGapsConfig:
    front: List[LipsGapSpanConfig] = None
    back: List[LipsGapSpanConfig] = None
    left: List[LipsGapSpanConfig] = None
    right: List[LipsGapSpanConfig] = None


@dataclass
class PlatformLipsConfig:
    front: bool = False
    back: bool = False
    left: bool = False
    right: bool = False
    gaps: List[LipGapsConfig] = None


@dataclass
class FloorTexturesConfig:
    material: str
    positions: List[Vector2dInt] = None


@dataclass
class ShowConfig:
    step_begin: int
    position: Vector3d = Vector3d(0, 0, 0)
    rotation: Vector3d = Vector3d(0, 0, 0)
    scale: Vector3d = Vector3d(1, 1, 1)
    bounding_box: List[dict] = field(default_factory=list)  # debug property


@dataclass
class SizeConfig:
    step_begin: int
    step_end: int
    size: Vector3d = Vector3d(1, 1, 1)
    repeat: bool = False
    step_wait: int = 0


@dataclass
class SingleStepConfig:
    step_begin: int


@dataclass
class StepBeginEndConfig:
    step_begin: int
    step_end: int
    repeat: bool = False
    step_wait: int = 0


@dataclass
class TeleportConfig:
    step_begin: int
    position: Vector3d = Vector3d(0, 0, 0)


@dataclass
class TransformConfig:
    position: Vector3d = Vector3d(0, 0, 0)
    rotation: Vector3d = Vector3d(0, 0, 0)
    scale: Vector3d = Vector3d(1, 1, 1)


@dataclass
class SceneObject:
    id: str
    type: str  # should this be an enum?
    center_of_mass: Vector3d = None
    change_materials: List[ChangeMaterialConfig] = None
    debug: dict = None
    forces: List[ForceConfig] = None
    ghosts: List[StepBeginEndConfig] = None
    hides: List[SingleStepConfig] = None
    kinematic: bool = None
    location_parent: str = None
    locked: bool = False
    mass: float = None
    materials: List[str] = None
    material_file: str = None  # deprecated; please use materials
    max_angular_velocity: float = None
    # Docs say moveable's default is dependant on type.  That could
    # be a problem for the concrete classes.  Needs more review later
    moveable: bool = None
    moves: List[MoveConfig] = None
    null_parent: TransformConfig = None
    openable: bool = None
    opened: bool = None
    open_close: List[OpenCloseConfig] = None
    lips: PlatformLipsConfig = None
    physics: bool = None
    physics_properties: PhysicsConfig = None
    pickupable: bool = None
    receptacle: bool = None
    reset_center_of_mass: bool = None
    resizes: List[SizeConfig] = None
    rotates: List[MoveConfig] = None
    salient_materials: List[str] = None
    seesaw: bool = None
    shows: List[ShowConfig] = None
    shrouds: List[StepBeginEndConfig] = None
    states: List[List[str]] = None
    structure: bool = None
    teleports: List[TeleportConfig] = None
    toggle_physics: List[SingleStepConfig] = None
    torques: List[ForceConfig] = None

    # These are deprecated, but needed for Eval 3 backwards compatibility
    can_contain_target: bool = None
    obstacle: bool = None
    occluder: bool = None
    position_y: float = None
    stack_target: bool = None


@dataclass
class SceneConfiguration:
    '''Class for keeping track of scene configuration'''
    ceiling_material: str = None
    debug: dict = None
    floor_material: str = None
    floor_properties: PhysicsConfig = None
    floor_textures: List[FloorTexturesConfig] = field(default_factory=list)
    goal: Goal = None  # TODO change to concrete class
    holes: List[Vector2dInt] = field(default_factory=list)
    intuitive_physics: bool = False
    isometric: bool = False
    lava: List[Vector2dInt] = field(default_factory=list)
    name: str = None
    objects: List[SceneObject] = field(default_factory=list)
    observation: bool = False  # deprecated; please use intuitivePhysics
    performer_start: PerformerStart = None
    restrict_open_doors: bool = None
    room_dimensions: Vector3d = field(
        default=ConfigManager.DEFAULT_ROOM_DIMENSIONS)
    room_materials: RoomMaterials = None
    screenshot: bool = False  # developer use only; for the image generator
    version: int = None
    wall_material: str = None
    wall_properties: PhysicsConfig = None

    # These are deprecated, but needed for Eval 3 backwards compatibility
    evaluation: str = None
    evaluation_only: bool = None
    eval_name: str = None
    hypercube_number: int = None
    scene_number: int = None
    sequence_number: int = None
    training: bool = None

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
