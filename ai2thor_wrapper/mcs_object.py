from mcs_material import MCS_Material
from mcs_util import MCS_Util

class MCS_Object:
    """
    Defines attributes of an object in the MCS 3D environment.

    Attributes
    ----------
    angle : dict
        The "x" & "y" degrees (or "x" & "z" degrees if in the "LIE" pose) needed to "RotateLook" to face this object.
    distance : float
        The distance to this object in number of steps ("Move" actions).
    held : boolean
        Whether you are holding this object.
    id : string
        The unique ID of this object, used with some actions.
    mass : float
        Haptic feedback.  The mass of this object.  Only returned in output while holding this object or from actions
        which involve touching this object.
    material : string
        Haptic feedback.  The material of this object.  Only returned in output while holding this object or from actions
        which involve touching this object.  See MCS_Material
    """

    def __init__(
        self,
        angle=None,
        distance=None,
        held=False,
        mass=None,
        material=MCS_Material.UNDEFINED,
        uuid=None
    ):
        self.angle = angle
        self.distance = distance
        self.held = held
        self.mass = mass
        self.material = material
        self.uuid = uuid

    def __str__(self):
        return MCS_Util.class_to_str(self)
