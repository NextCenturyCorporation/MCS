from mcs_material import MCS_Material
from mcs_util import MCS_Util

class MCS_Object:

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
