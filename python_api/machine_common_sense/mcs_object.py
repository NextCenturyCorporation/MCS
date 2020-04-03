from machine_common_sense.mcs_material import MCS_Material
from machine_common_sense.mcs_util import MCS_Util


class MCS_Object(object):
    """
    Defines attributes of an object in the MCS 3D environment.

    Attributes
    ----------
    uuid : string
        The unique ID of this object, used with some actions.
    color : dict
        The "r", "g", and "b" pixel values of this object in images from the MCS_Step_Output's "object_mask_list".
    direction : dict
        The normalized direction vector of "x", "y", and "z" degrees between your position and this object's.
        Use "x" and "y" as "rotation" and "horizon" params (respectively) in a "RotateLook" action to face this object.
    distance : float
        The distance along the 2-dimensional X/Z grid from you oto this object in number of steps ("Move" actions).
    held : boolean
        Whether you are holding this object.
    mass : float
        Haptic feedback.  The mass of this object.
    material_list : list of strings
        Haptic feedback.  The material(s) of this object.  See MCS_Material.
    point_list : list of dicts
        The list of 3D points (dicts with "x", "y", and "z") that form the outer shape of this object.
    position : dict
        The "x", "y", and "z" coordinates for the global position of the center of this object's 3D model.
    rotation : float
        This object's rotation angle in degrees.
    visible : boolean
        Whether you can see this object in your camera viewport.
    """

    def __init__(
        self,
        uuid="",
        color={},
        direction={},
        distance=-1.0,
        held=False,
        mass=0.0,
        material_list=[],
        point_list=[],
        position={},
        rotation=0.0,
        visible=False
    ):
        self.uuid = uuid
        self.color = color
        self.direction = direction
        self.distance = distance
        self.held = held
        self.mass = mass
        self.material_list = material_list
        self.point_list = point_list
        self.position = position
        self.rotation = rotation
        self.visible = visible

    def __str__(self):
        return MCS_Util.class_to_str(self)
