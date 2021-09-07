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

    @staticmethod
    def verify_material_enum_string(enum_string):
        """
        Returns whether the given string can be successfully converted into an
        Material enum.

        Parameters
        ----------
        enum_string
            The string to be converted into an Material enum.

        Returns
        -------
        boolean
        """
        try:
            enum_instance = Material[enum_string.upper()]  # noqa: F841
            return True
        except KeyError:
            return False
