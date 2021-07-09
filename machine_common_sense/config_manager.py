import ast
import configparser  # noqa: F401
import logging
import os
from dataclasses import dataclass, field
from typing import List

import numpy as np
import yaml  # noqa: F401
from marshmallow import Schema, fields, post_load

from .action import Action
from .goal_metadata import GoalMetadata

logger = logging.getLogger(__name__)


class ConfigManager(object):

    DEFAULT_CLIPPING_PLANE_FAR = 15.0
    # Normal metadata plus metadata for all hidden objects
    CONFIG_METADATA_TIER_ORACLE = 'oracle'
    # No metadata, except for the images, depth masks, object masks,
    # and haptic/audio feedback
    CONFIG_METADATA_TIER_LEVEL_2 = 'level2'
    # No metadata, except for the images, depth masks, and haptic/audio
    # feedback
    CONFIG_METADATA_TIER_LEVEL_1 = 'level1'
    # No metadata, except for the images and haptic/audio
    # feedback
    CONFIG_METADATA_TIER_NONE = 'none'

    # Default metadata level if none specified, meant for use during
    # development
    CONFIG_METADATA_TIER_DEFAULT = 'default'

    CONFIG_FILE_ENV_VAR = 'MCS_CONFIG_FILE_PATH'
    METADATA_ENV_VAR = 'MCS_METADATA_LEVEL'
    DEFAULT_CONFIG_FILE = './mcs_config.ini'

    CONFIG_DEFAULT_SECTION = 'MCS'

    CONFIG_AWS_ACCESS_KEY_ID = 'aws_access_key_id'
    CONFIG_AWS_SECRET_ACCESS_KEY = 'aws_secret_access_key'
    CONFIG_EVALUATION = 'evaluation'
    CONFIG_EVALUATION_NAME = 'evaluation_name'
    CONFIG_HISTORY_ENABLED = 'history_enabled'
    CONFIG_METADATA_TIER = 'metadata'
    CONFIG_NOISE_ENABLED = 'noise_enabled'
    CONFIG_S3_BUCKET = 's3_bucket'
    CONFIG_S3_FOLDER = 's3_folder'
    CONFIG_SAVE_DEBUG_IMAGES = 'save_debug_images'
    CONFIG_SAVE_DEBUG_JSON = 'save_debug_json'
    CONFIG_SEED = 'seed'
    CONFIG_SIZE = 'size'
    CONFIG_TEAM = 'team'
    CONFIG_VIDEO_ENABLED = 'video_enabled'

    # Please keep the aspect ratio as 3:2 because the IntPhys scenes are built
    # on this assumption.
    SCREEN_WIDTH_DEFAULT = 600
    SCREEN_WIDTH_MIN = 450

    def __init__(self, config_file_path=None):
        # For config file, look for environment variable first,
        # then look for config_path parameter from constructor
        self._config_file = os.getenv(
            self.CONFIG_FILE_ENV_VAR, config_file_path)

        if(self._config_file is None):
            self._config_file = self.DEFAULT_CONFIG_FILE

        self._read_config_file()

        self._validate_screen_size()

    def _read_config_file(self):
        self._config = configparser.ConfigParser()
        if os.path.exists(self._config_file):
            self._config.read(self._config_file)
            logger.info('Config File Path: ' + self._config_file)
        else:
            logger.info('No Config File')

    def _validate_screen_size(self):
        if(self.get_size() < self.SCREEN_WIDTH_MIN):
            self._config.set(
                self.CONFIG_DEFAULT_SECTION,
                self.CONFIG_SIZE,
                str(self.SCREEN_WIDTH_DEFAULT)
            )

    def get_aws_access_key_id(self):
        return self._config.get(
            self.CONFIG_DEFAULT_SECTION,
            self.CONFIG_AWS_ACCESS_KEY_ID,
            fallback=None
        )

    def get_aws_secret_access_key(self):
        return self._config.get(
            self.CONFIG_DEFAULT_SECTION,
            self.CONFIG_AWS_SECRET_ACCESS_KEY,
            fallback=None
        )

    def get_evaluation_name(self):
        return self._config.get(
            self.CONFIG_DEFAULT_SECTION,
            self.CONFIG_EVALUATION_NAME,
            fallback=''
        )

    def get_metadata_tier(self):
        # Environment variable override for metadata property
        metadata_env_var = os.getenv('MCS_METADATA_LEVEL', None)

        if(metadata_env_var is None):
            return self._config.get(
                self.CONFIG_DEFAULT_SECTION,
                self.CONFIG_METADATA_TIER,
                fallback='default'
            )

        return metadata_env_var

    def set_metadata_tier(self, mode):
        self._config.set(
            self.CONFIG_DEFAULT_SECTION,
            self.CONFIG_METADATA_TIER,
            mode
        )

    def get_s3_bucket(self):
        return self._config.get(
            self.CONFIG_DEFAULT_SECTION,
            self.CONFIG_S3_BUCKET,
            fallback=None
        )

    def get_s3_folder(self):
        return self._config.get(
            self.CONFIG_DEFAULT_SECTION,
            self.CONFIG_S3_FOLDER,
            fallback=None
        )

    def get_seed(self):
        return self._config.getint(
            self.CONFIG_DEFAULT_SECTION,
            self.CONFIG_SEED,
            fallback=None
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

    def is_evaluation(self):
        return self._config.getboolean(
            self.CONFIG_DEFAULT_SECTION,
            self.CONFIG_EVALUATION,
            fallback=False
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
        if(metadata_tier == self.CONFIG_METADATA_TIER_LEVEL_1 or
           metadata_tier == self.CONFIG_METADATA_TIER_LEVEL_2 or
           metadata_tier == self.CONFIG_METADATA_TIER_ORACLE):
            return True
        else:
            return False

    def is_object_masks_enabled(self) -> bool:
        metadata_tier = self.get_metadata_tier()
        if(metadata_tier == self.CONFIG_METADATA_TIER_LEVEL_1):
            return False
        elif(metadata_tier == self.CONFIG_METADATA_TIER_LEVEL_2 or
             metadata_tier == self.CONFIG_METADATA_TIER_ORACLE):
            return True
        else:
            return False

    def get_screen_width(self) -> int:
        return self.get_size()

    def get_screen_height(self) -> int:
        size = self.get_size()
        return int(size / 3 * 2)


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
    domainsInfo = fields.Dict()  # UI property
    habituation_total = fields.Int()
    info_list = fields.List(fields.Str())
    last_preview_phase_step = fields.Int()
    last_step = fields.Int()
    metadata = fields.Dict()
    objectsInfo = fields.Dict()  # UI property
    sceneInfo = fields.Dict()  # UI property
    skip_preview_phase = fields.Bool()
    task_list = fields.List(fields.Str())
    type_list = fields.List(fields.Str())

    @post_load
    def make_goal(self, data, **kwargs):
        return Goal(**data)


class ChangeMaterialConfigSchema(Schema):
    stepBegin = fields.Int()
    materials = fields.List(fields.Str())

    @post_load
    def make_change_material(self, data, **kwargs):
        return ChangeMaterialConfig(**data)


class ForceConfigSchema(Schema):
    stepBegin = fields.Int()
    stepEnd = fields.Int()
    vector = fields.Nested(Vector3dSchema)
    relative = fields.Bool()

    @post_load
    def make_force_config(self, data, **kwargs):
        return ForceConfig(**data)


class MoveConfigSchema(Schema):
    stepBegin = fields.Int()
    stepEnd = fields.Int()
    vector = fields.Nested(Vector3dSchema)

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
    angularDrag = fields.Float()
    bounciness = fields.Float()
    drag = fields.Float()
    dynamicFriction = fields.Float()
    staticFriction = fields.Float()

    @post_load
    def make_physics_config(self, data, **kwargs):
        return PhysicsConfig(**data)


class ShowConfigSchema(Schema):
    stepBegin = fields.Int()
    position = fields.Nested(Vector3dSchema)
    rotation = fields.Nested(Vector3dSchema)
    scale = fields.Nested(Vector3dSchema)
    boundingBox = fields.List(fields.Dict())  # debug property

    @post_load
    def make_show_config(self, data, **kwargs):
        return ShowConfig(**data)


class SizeConfigSchema(Schema):
    stepBegin = fields.Int()
    stepEnd = fields.Int()
    size = fields.Nested(Vector3dSchema)

    @post_load
    def make_size_config(self, data, **kwargs):
        return SizeConfig(**data)


class SingleStepConfigSchema(Schema):
    stepBegin = fields.Int()

    @post_load
    def make_single_step_config(self, data, **kwargs):
        return SingleStepConfig(**data)


class StepBeginEndConfigSchema(Schema):
    stepBegin = fields.Int()
    stepEnd = fields.Int()

    @post_load
    def make_step_begin_end_config(self, data, **kwargs):
        return StepBeginEndConfig(**data)


class TeleportConfigSchema(Schema):
    stepBegin = fields.Int()
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
    centerOfMass = fields.Nested(Vector3dSchema)
    changeMaterials = fields.List(fields.Nested(ChangeMaterialConfigSchema))
    debug = fields.Dict()
    forces = fields.List(fields.Nested(ForceConfigSchema))
    ghosts = fields.List(fields.Nested(StepBeginEndConfigSchema))
    hides = fields.List(fields.Nested(SingleStepConfigSchema))
    kinematic = fields.Bool()
    locationParent = fields.Str()
    mass = fields.Float()
    materials = fields.List(fields.Str())
    materialFile = fields.Str()  # deprecated; please use materials
    moveable = fields.Bool()
    moves = fields.List(fields.Nested(MoveConfigSchema))
    nullParent = fields.Nested(TransformConfigSchema)
    openable = fields.Bool()
    opened = fields.Bool()
    openClose = fields.List(fields.Nested(OpenCloseConfigSchema))
    physics = fields.Bool()
    physicsProperties = fields.Nested(PhysicsConfigSchema)
    pickupable = fields.Bool()
    receptacle = fields.Bool()
    resetCenterOfMass = fields.Bool()
    resizes = fields.List(fields.Nested(SizeConfigSchema))
    rotates = fields.List(fields.Nested(MoveConfigSchema))
    salientMaterials = fields.List(fields.Str())
    shows = fields.List(fields.Nested(ShowConfigSchema))
    shrouds = fields.List(fields.Nested(StepBeginEndConfigSchema))
    states = fields.List(fields.List(fields.Str(), allow_none=True))
    structure = fields.Bool()
    teleports = fields.List(fields.Nested(TeleportConfigSchema))
    togglePhysics = fields.List(fields.Nested(SingleStepConfigSchema))
    torques = fields.List(fields.Nested(MoveConfigSchema))

    # These are deprecated, but needed for Eval 3 backwards compatibility
    canContainTarget = fields.Bool()
    obstacle = fields.Bool()
    occluder = fields.Bool()
    positionY = fields.Float()
    stackTarget = fields.Bool()

    @post_load
    def make_scene_object(self, data, **kwargs):
        return SceneObject(**data)


class SceneConfigurationSchema(Schema):
    # The passive agent scenes can have a None ceilingMaterial
    ceilingMaterial = fields.Str(allow_none=True)
    debug = fields.Dict()
    floorMaterial = fields.Str()
    floorProperties = fields.Nested(PhysicsConfigSchema)
    goal = fields.Nested(GoalSchema)
    intuitivePhysics = fields.Bool()
    isometric = fields.Bool()
    name = fields.Str()
    objects = fields.List(fields.Nested(SceneObjectSchema))
    observation = fields.Bool()  # deprecated; please use intuitivePhysics
    performerStart = fields.Nested(PerformerStartSchema)
    roomDimensions = fields.Nested(Vector3dSchema)
    roomMaterials = fields.Nested(RoomMaterialsSchema)
    screenshot = fields.Bool()  # developer use only; for the image generator
    version = fields.Integer()
    wallMaterial = fields.Str()
    wallProperties = fields.Nested(PhysicsConfigSchema)

    # These are deprecated, but needed for Eval 3 backwards compatibility
    evaluation = fields.Str(allow_none=True)
    evaluationOnly = fields.Bool()
    evalName = fields.Str()
    hypercubeNumber = fields.Int()
    sceneNumber = fields.Int()
    sequenceNumber = fields.Int()
    training = fields.Bool()

    @post_load
    def make_scene_configuration(self, data, **kwargs):
        return SceneConfiguration(**data)


@dataclass
class Vector3d:
    # There is probably a class like this in python somewhere
    # but i don't know where it is.
    # TODO change later, potentially rename?
    x: float = 0
    y: float = 0
    z: float = 0


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
    domainsInfo: dict = None  # UI property
    habituation_total: int = None
    info_list: list = None
    last_preview_phase_step: int = None
    last_step: int = None
    # TODO metadata objects
    metadata: dict = None
    objectsInfo: dict = None  # UI property
    sceneInfo: dict = None  # UI property
    skip_preview_phase: bool = False
    task_list: List[str] = None
    type_list: List[str] = None


@dataclass
class ChangeMaterialConfig:
    stepBegin: int
    materials: List[str]


@dataclass
class ForceConfig:
    stepBegin: int
    stepEnd: int
    vector: Vector3d = Vector3d(0, 0, 0)
    relative: bool = False


@dataclass
class MoveConfig:
    stepBegin: int
    stepEnd: int
    vector: Vector3d = Vector3d(0, 0, 0)


@dataclass
class OpenCloseConfig:
    step: int
    open: bool


@dataclass
class PhysicsConfig:
    enable: bool = False
    angularDrag: float = None
    bounciness: float = None
    drag: float = None
    dynamicFriction: float = None
    staticFriction: float = None


@dataclass
class ShowConfig:
    stepBegin: int
    position: Vector3d = Vector3d(0, 0, 0)
    rotation: Vector3d = Vector3d(0, 0, 0)
    scale: Vector3d = Vector3d(1, 1, 1)
    boundingBox: List[dict] = field(default_factory=list)  # debug property


@dataclass
class SizeConfig:
    stepBegin: int
    stepEnd: int
    size: Vector3d = Vector3d(1, 1, 1)


@dataclass
class SingleStepConfig:
    stepBegin: int


@dataclass
class StepBeginEndConfig:
    stepBegin: int
    stepEnd: int


@dataclass
class TeleportConfig:
    stepBegin: int
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
    centerOfMass: Vector3d = None
    changeMaterials: List[ChangeMaterialConfig] = None
    debug: dict = None
    forces: List[ForceConfig] = None
    ghosts: List[StepBeginEndConfig] = None
    hides: List[SingleStepConfig] = None
    kinematic: bool = None
    locationParent: str = None
    mass: float = None
    materials: List[str] = None
    materialFile: str = None  # deprecated; please use materials
    # Docs say moveable's default is dependant on type.  That could
    # be a problem for the concrete classes.  Needs more review later
    moveable: bool = None
    moves: List[MoveConfig] = None
    nullParent: TransformConfig = None
    openable: bool = None
    opened: bool = None
    openClose: List[OpenCloseConfig] = None
    physics: bool = None
    physicsProperties: PhysicsConfig = None
    pickupable: bool = None
    receptacle: bool = None
    resetCenterOfMass: bool = None
    resizes: List[SizeConfig] = None
    rotates: List[MoveConfig] = None
    salientMaterials: List[str] = None
    shows: List[ShowConfig] = None
    shrouds: List[StepBeginEndConfig] = None
    states: List[List[str]] = None
    structure: bool = None
    teleports: List[TeleportConfig] = None
    togglePhysics: List[SingleStepConfig] = None
    torques: List[MoveConfig] = None

    # These are deprecated, but needed for Eval 3 backwards compatibility
    canContainTarget: bool = None
    obstacle: bool = None
    occluder: bool = None
    positionY: float = None
    stackTarget: bool = None


@dataclass
class SceneConfiguration:
    '''Class for keeping track of scene configuration'''
    ceilingMaterial: str = None
    debug: dict = None
    floorMaterial: str = None
    floorProperties: PhysicsConfig = None
    goal: Goal = None  # TODO change to concrete class
    intuitivePhysics: bool = False
    isometric: bool = False
    name: str = None
    objects: List[SceneObject] = field(default_factory=list)
    observation: bool = False  # deprecated; please use intuitivePhysics
    performerStart: PerformerStart = None
    roomDimensions: Vector3d = None
    roomMaterials: RoomMaterials = None
    screenshot: bool = False  # developer use only; for the image generator
    version: int = None
    wallMaterial: str = None
    wallProperties: PhysicsConfig = None

    # These are deprecated, but needed for Eval 3 backwards compatibility
    evaluation: str = None
    evaluationOnly: bool = None
    evalName: str = None
    hypercubeNumber: int = None
    sceneNumber: int = None
    sequenceNumber: int = None
    training: bool = None

    def retrieve_object_states(self,
                               object_id, step_number):
        """Return the state list at the current step for the object with the
        given ID from the scene configuration data, if any."""
        state_list_each_step = []
        # Retrieve the object's states from the scene configuration.
        for object_config in self.objects:
            if object_config.id == object_id:
                state_list_each_step = (
                    object_config.states if object_config.states else []
                )
                break
        # Retrieve the object's states in the current step.
        if len(state_list_each_step) > step_number:
            state_list = state_list_each_step[step_number]
            # Validate the data type.
            if state_list is not None:
                if not isinstance(state_list, list):
                    return [state_list]
                return [str(state) for state in state_list]
        return []

    def retrieve_goal(self):
        if not self.goal:
            return self.update_goal_target_image(GoalMetadata())

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

        return self.update_goal_target_image(GoalMetadata(
            action_list=(action_list if action_list else None),
            category=goal.category or '',
            description=goal.description or '',
            habituation_total=goal.habituation_total or 0,
            last_preview_phase_step=(goal.last_preview_phase_step or 0),
            last_step=goal.last_step or None,
            metadata=goal.metadata or {}
        ))

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
