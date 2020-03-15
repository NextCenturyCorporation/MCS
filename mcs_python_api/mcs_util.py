from mcs_material import MCS_Material

class MCS_Util:
    """
    Defines utility functions for MCS classes.
    """

    NUMBER_OF_SPACES = 4

    """
    Transforms the given class into a string.

    Parameters
    ----------
    input_value
        The input class.
    depth : int, optional
        The indent depth (default 0).

    Returns
    -------
    string
    """
    @staticmethod
    def class_to_str(input_class, depth=0):
        this_indent = " " * MCS_Util.NUMBER_OF_SPACES * depth
        next_indent = " " * MCS_Util.NUMBER_OF_SPACES * (depth + 1)
        text_list = []
        props = {prop_key:prop_value for prop_key, prop_value in vars(input_class).items() if not \
                prop_key.startswith('_') or callable(prop_value)}
        for prop_key, prop_value in props.items():
            text_list.append(next_indent + "\"" + prop_key + "\": " + MCS_Util.value_to_str(prop_value, depth + 1))
        return "{}" if len(text_list) == 0 else "{\n" + (",\n").join(text_list) + "\n" + this_indent + "}"

    """
    Transforms the given list of MCS_Object objects into a list of strings.

    Parameters
    ----------
    object_list : list of MCS_Object objects
        The input list.

    Returns
    -------
    list of strings
    """
    @staticmethod
    def generate_pretty_object_output(object_list):
        # TODO What else should we show here?
        titles = ["OBJECT ID", "HELD", "VISIBLE", "DISTANCE", "DIRECTION"]
        rows = [titles] + [[metadata.uuid, metadata.held, metadata.visible, metadata.distance, \
                MCS_Util.vector_to_string(metadata.direction)] for metadata in object_list]
        widths = [max(len(str(row[i])) for row in rows) for i in range(0, len(titles))]
        return [("  ".join(str(row[i]).ljust(widths[i]) for i in range(0, len(row)))) for row in rows]

    """
    Transforms the given value into a string.

    Parameters
    ----------
    input_value
        The input value.
    depth : int, optional
        The indent depth (default 0).

    Returns
    -------
    string
    """
    @staticmethod
    def value_to_str(input_value, depth=0):
        this_indent = " " * MCS_Util.NUMBER_OF_SPACES * depth
        next_indent = " " * MCS_Util.NUMBER_OF_SPACES * (depth + 1)
        if isinstance(input_value, dict):
            text_list = []
            for dict_key, dict_value in input_value.items():
                text_list.append(next_indent + "\"" + dict_key + "\": " + MCS_Util.value_to_str(dict_value, depth + 1))
            return "{}" if len(text_list) == 0 else "{\n" + (",\n").join(text_list) + "\n" + this_indent + "}"
        if isinstance(input_value, list):
            text_list = []
            for list_item in input_value:
                text_list.append(next_indent + MCS_Util.value_to_str(list_item, depth + 1))
            return "[]" if len(text_list) == 0 else "[\n" + (",\n").join(text_list) + "\n" + this_indent + "]"
        elif isinstance(input_value, str):
            return "\"" + input_value.replace("\"", "\\\"") + "\""
        return str(input_value).replace("\n", "\n" + this_indent)

    """
    Transforms the given vector into a string.

    Parameters
    ----------
    vector : dict
        The input vector.

    Returns
    -------
    string
    """
    @staticmethod
    def vector_to_string(vector):
        return ('(' + str(vector['x']) + ',' + str(vector['y']) + ',' + str(vector['z']) + ')') if vector is not None \
                else 'None'

    """
    Returns whether the given string can be successfully converted into an MCS_Material enum.

    Parameters
    ----------
    enum_string
        The string to be converted into an MCS_Material enum.

    Returns
    -------
    boolean
    """
    @staticmethod
    def verify_material_enum_string(enum_string):
        try:
            enum_instance = MCS_Material[enum_string.upper()]
            return True
        except KeyError:
            return False

