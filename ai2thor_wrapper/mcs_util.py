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

