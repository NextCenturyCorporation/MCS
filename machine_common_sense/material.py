from enum import Enum, unique


@unique
class Material(Enum):
    """
    Possible materials of objects. An object can have one or more materials.
    """

    CERAMIC = "CERAMIC"
    """"""

    FABRIC = "FABRIC"
    """"""

    FOOD = "FOOD"
    """"""

    GLASS = "GLASS"
    """"""

    METAL = "METAL"
    """"""

    ORGANIC = "ORGANIC"
    """"""

    PAPER = "PAPER"
    """"""

    PLASTIC = "PLASTIC"
    """"""

    RUBBER = "RUBBER"
    """"""

    SOAP = "SOAP"
    """"""

    SPONGE = "SPONGE"
    """"""

    STONE = "STONE"
    """"""

    UNDEFINED = "UNDEFINED"
    """"""

    WAX = "WAX"
    """"""

    WOOD = "WOOD"
    """"""
