import copy

from .goal_metadata import GoalMetadata
from .return_status import ReturnStatus
from .stringifier import Stringifier


class StepMetadata:
    """
    Defines output metadata from an action step in the MCS 3D environment.

    Attributes
    ----------
    action_list : list of (string, dict) tuples
        The list of all actions that are available for the next step.
        Each action is returned as a tuple containing the action string and
        the action's restricted parameters, if any.
        For example: ("Pass", {}) forces a Pass action; ("PickupObject", {})
        forces a PickupObject action with any parameters; and
        ("PickupObject", {"objectId": "a"}) forces a PickupObject action with
        the specific parameters objectId=a.
        EndHabituation is a special case of the action_list where its
        parameters will always be empty. When taking the EndHabituation
        action, the MCS system may apply hidden displacement parameters to the
        robot.
        An action_list of None or an empty list means that all actions will
        be available for the next step.

        To "step" using the first action from the action_list:

        .. highlight:: python
        .. code-block:: python

            step_metadata = controller.start_scene(scene_data)
            action, params = step_metadata.action_list[0]
            step_metadata = controller.step(action, **params)

        Derived from :mod:`GoalMetadata.action_list[step_number]
        <machine_common_sense.GoalMetadata>`.
        May be a subset of all possible actions. See
        :mod:`Action <machine_common_sense.Action>`.
    camera_aspect_ratio : (float, float)
        The player camera's aspect ratio. This will remain constant for the
        whole scene.
    camera_clipping_planes : (float, float)
        The player camera's near and far clipping planes, in meters. This will
        remain constant for the whole scene. Default (0.01, 150)
    camera_field_of_view : float
        The player camera's field of view. This will remain constant for
        the whole scene.
    camera_height : float
        The player camera's height, in meters.
    depth_map_list : list of 2D numpy arrays
        The list of 2-dimensional numpy arrays of depth float data from the
        scene after the last action and physics simulation were run. This is
        usually a list with 1 array, except for the output from start_scene
        for a scene with a scripted Preview Phase (Preview Phase case details
        TBD).
        Each 32-bit depth float in the 2-dimensional numpy array is a value
        between the camera's near clipping plane (default 0.01) and the
        camera's far clipping plane (default 150) corresponding to the depth,
        in meters, at that pixel in the image.
        Note that this list will be empty if the metadata level is 'none'.
    goal : GoalMetadata or None
        The goal for the whole scene. Will be None in "Exploration" scenes.
    haptic_feedback : dict
        Haptic feedback sources for the agent. Values are true or false
        depending on if the agent is touching the haptic feedback source.
        The only current supported contact is "on_lava"
    habituation_trial : int or None
        The current habituation trial (as a positive integer), or None if the
        scene is not currently in a habituation trial (meaning this scene is
        in a test trial).
    head_tilt : float
        How far your head is tilted up/down in degrees (between 90 and -90).
        Changed by setting the "horizon" parameter in a "RotateLook" action.
    holes : list of tuples
        Coordinates of holes as (X, Z) float tuples. Will be set to 'None' if
        using a metadata level below the 'oracle' level.
    image_list : list of Pillow.Image objects
        The list of images from the scene after the last action and physics
        simulation were run. This is usually a list with 1 image, except for
        the output from start_scene for a scene with a scripted Preview Phase.
        (Preview Phase case details TBD).
    lava : list of tuples
        Coordinates of pools of lava as (X1, Z1, X2, Z2) float tuples, where
        X1/Z1 is the top-left corner and X2/Z2 is the bottom-right conrer. Will
        be set to 'None' if using a metadata level below the 'oracle' level.
    object_list : list of ObjectMetadata objects
        The list of metadata for all the visible interactive objects in the
        scene. This list will be empty if using a metadata level below
        the 'oracle' level. For metadata on structural objects like walls,
        please see structural_object_list
    object_mask_list : list of Pillow.Image objects
        The list of object mask (instance segmentation) images from the scene
        after the last action and physics simulation were run. This is usually
        a list with 1 image, except for the output from start_scene for a
        scene with a scripted Preview Phase (Preview Phase case details TBD).
        The color of each object in the mask corresponds to the "color"
        property in its ObjectMetadata object.
        Note that this list will be empty if the metadata level is 'none'
        or 'level1'.
    performer_radius: float
        The radius of the performer, in meters.
    performer_reach: float
        The max reach of the performer, in meters.
    position : dict
        The "x", "y", and "z" coordinates for your global position.
        Will be set to 'None' if using a metadata level below the
        'oracle' level.
    resolved_object : string
        The object that was selected based on objectImageCoords
    resolved_receptacle_object_id : string
        The receptacle that was selected based on receptacleObjectImageCoords
    return_status : string
        The return status from your last action. See
        :mod:`Action <machine_common_sense.Action>`.
    reward : integer
        Reward is 1 on successful completion of a task, 0 otherwise.
    rotation : float
        Your current rotation angle in degrees. Will be set to 'None'
        if using a metadata level below the 'oracle' level.
    step_number : integer
        The step number of your last action, recorded since you started the
        current scene.
    steps_in_lava : integer
        The number of steps the agent has touched lava
    physics_frames_per_second : float
        The frames per second of the physics engine
    structural_object_list : list of ObjectMetadata objects
        The list of metadata for all the visible structural objects (like
        walls, occluders, and ramps) in the scene. This list will be empty
        if using a metadata level below the 'oracle' level.
        Occluders are composed of two separate objects,
        the "wall" and the "pole", with corresponding object IDs
        (occluder_wall_<uuid> and occluder_pole_<uuid>), and ramps are
        composed of between one and three objects (depending on the type
        of ramp), with corresponding object IDs.
    """

    def __init__(
        self,
        action_list=None,
        camera_aspect_ratio=None,
        camera_clipping_planes=None,
        camera_field_of_view=0.0,
        camera_height=0.0,
        depth_map_list=None,
        goal=None,
        habituation_trial=None,
        haptic_feedback=None,
        head_tilt=0.0,
        holes=None,
        image_list=None,
        lava=None,
        object_list=None,
        object_mask_list=None,
        performer_radius=0.0,
        performer_reach=0.0,
        physics_frames_per_second=0,
        position=None,
        resolved_object='',
        resolved_receptacle='',
        return_status=ReturnStatus.UNDEFINED.value,
        reward=0,
        rotation=0.0,
        step_number=0,
        steps_on_lava=0,
        structural_object_list=None
    ):
        self.action_list = [] if action_list is None else action_list
        self.camera_aspect_ratio = (
            0.0, 0.0) if camera_aspect_ratio is None else camera_aspect_ratio
        self.camera_clipping_planes = (
            (0.0, 0.0)
            if camera_clipping_planes is None
            else camera_clipping_planes
        )
        self.camera_field_of_view = camera_field_of_view
        self.camera_height = camera_height
        self.depth_map_list = (
            [] if depth_map_list is None else depth_map_list
        )
        self.goal = GoalMetadata() if goal is None else goal
        self.habituation_trial = habituation_trial
        self.haptic_feedback = (
            {} if haptic_feedback is None else haptic_feedback
        )
        self.head_tilt = head_tilt
        self.holes = [] if holes is None else holes
        self.image_list = [] if image_list is None else image_list
        self.lava = [] if lava is None else lava
        self.object_list = [] if object_list is None else object_list
        self.object_mask_list = (
            [] if object_mask_list is None else object_mask_list
        )
        self.performer_radius = performer_radius
        self.performer_reach = performer_reach
        self.physics_frames_per_second = physics_frames_per_second
        self.position = {} if position is None else position
        self.resolved_object = resolved_object
        self.resolved_receptacle = resolved_receptacle
        self.return_status = return_status
        self.reward = reward
        self.rotation = rotation
        self.step_number = step_number
        self.steps_on_lava = steps_on_lava
        self.structural_object_list = [
        ] if structural_object_list is None else structural_object_list

    def __str__(self):
        return Stringifier.class_to_str(self)

    def check_list_none(self, obj_list):
        if obj_list is None:
            return None
        else:
            return {obj.uuid: dict(obj) for obj in obj_list}

    def copy_without_depth_or_images(self):
        """Return a deep copy of this StepMetadata with default depth_map_list,
        image_list, and object_mask_list properties."""
        step_metadata_copy = StepMetadata()
        # This class's __iter__ function will ignore specific properties.
        for key, _ in self:
            setattr(step_metadata_copy, key, copy.deepcopy(getattr(self, key)))
        return step_metadata_copy

    # Allows converting the class to a dictionary, along with allowing
    #   certain fields to be left out of output file
    def __iter__(self):
        yield 'action_list', self.action_list
        yield 'camera_aspect_ratio', self.camera_aspect_ratio
        yield 'camera_clipping_planes', self.camera_clipping_planes
        yield 'camera_field_of_view', self.camera_field_of_view
        yield 'camera_height', self.camera_height
        # Intentionally no depth_map_list
        yield 'goal', dict(self.goal)
        yield 'habituation_trial', self.habituation_trial
        yield 'haptic_feedback', self.haptic_feedback
        yield 'head_tilt', self.head_tilt
        # Intentionally no image_list
        yield 'object_list', self.check_list_none(self.object_list)
        # Intentionally no object_mask_list
        yield 'performer_radius', self.performer_radius
        yield 'performer_reach', self.performer_reach
        yield 'physics_frames_per_second', self.physics_frames_per_second
        yield 'position', self.position
        yield 'resolved_object', self.resolved_object
        yield 'resolved_receptacle', self.resolved_receptacle
        yield 'return_status', self.return_status
        yield 'reward', self.reward
        yield 'rotation', self.rotation
        yield 'step_number', self.step_number,
        yield 'steps_on_lava', self.steps_on_lava,
        yield 'structural_object_list', self.check_list_none(
            self.structural_object_list)
