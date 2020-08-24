from enum import Enum, unique


@unique
class MCS_Material(Enum):
    """
    Possible materials of objects. An object can have one or more materials.
    """

    CERAMIC = "CERAMIC"
    """
    Ceramic.
    """

    FABRIC = "FABRIC"
    """
    Fabric.
    """

    FOOD = "FOOD"
    """
    Food.
    """

    GLASS = "GLASS"
    """
    Glass.
    """

    METAL = "METAL"
    """
    Metal.
    """

    ORGANIC = "ORGANIC"
    """
    Organic.
    """

    PAPER = "PAPER"
    """
    Paper.
    """

    PLASTIC = "PLASTIC"
    """
    Plastic.
    """

    RUBBER = "RUBBER"
    """
    Rubber.
    """

    SOAP = "SOAP"
    """
    Soap.
    """

    SPONGE = "SPONGE"
    """
    Sponge.
    """

    STONE = "STONE"
    """
    Stone.
    """

    UNDEFINED = "UNDEFINED"
    """
    Undefined.
    """

    WAX = "WAX"
    """
    Wax.
    """

    WOOD = "WOOD"
    """
    Wood.
    """
