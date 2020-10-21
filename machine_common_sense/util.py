import numpy

from .action import Action
from .material import Material


class Util:
    """
    Defines utility functions for MCS classes.
    """

    NUMBER_OF_SPACES = 4

    @staticmethod
    def class_to_str(input_class, depth=0):
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
        this_indent = " " * Util.NUMBER_OF_SPACES * depth
        next_indent = " " * Util.NUMBER_OF_SPACES * (depth + 1)
        text_list = []
        props = {
            prop_key: prop_value
            for prop_key, prop_value in vars(input_class).items()
            if not prop_key.startswith('_') or callable(prop_value)
        }
        for prop_key, prop_value in props.items():
            text_list.append(
                next_indent +
                "\"" +
                prop_key +
                "\": " +
                Util.value_to_str(
                    prop_value,
                    depth +
                    1))
        return "{}" if len(text_list) == 0 else "{\n" + \
            (",\n").join(text_list) + "\n" + this_indent + "}"

    @staticmethod
    def generate_pretty_object_output(object_list):
        """
        Transforms the given list of ObjectMetadata objects into a
        list of strings.

        Parameters
        ----------
        object_list : list of ObjectMetadata objects
            The input list.

        Returns
        -------
        list of strings
        """
        # TODO What else should we show here?
        titles = [
            "OBJECT ID",
            "SHAPE",
            "COLORS",
            "HELD",
            "POSITION (WORLD)",
            "DIMENSIONS (WORLD)",
            "DISTANCE (WORLD)",
            "DIRECTION (WORLD)"]
        rows = [titles] + [
            [
                metadata.uuid,
                metadata.shape,
                ", ".join(
                    metadata.texture_color_list) if(
                    metadata.texture_color_list is not None) else metadata.texture_color_list,  # noqa: E501
                metadata.held,
                Util.vector_to_string(metadata.position),
                Util.vector_to_string(metadata.dimensions),
                metadata.distance_in_world,
                Util.vector_to_string(metadata.direction)
            ]
            for metadata in object_list
        ]
        widths = [max(len(str(row[i])) for row in rows)
                  for i in range(0, len(titles))]
        return [("  ".join(str(row[i]).ljust(widths[i])
                           for i in range(0, len(row)))) for row in rows]

    @staticmethod
    def input_to_action_and_params(input_str):
        """
        Transforms the given input string into an action string
        and parameter dict.

        Parameters
        ----------
        input_value : string
            The input value.

        Returns
        -------
        string
            The action string, or None if the given input had an error
            transforming the action string.
        dict
            The parameter dict, or None if the given input had an error
            transforming parameters.
        """
        input_split = input_str.split(',')
        action = input_split[0]

        try:
            validate_action = Action(action).name  # noqa: F841
        except BaseException:
            return None, {}

        if len(input_split) < 2:
            return action, {}

        params = {}

        try:
            for param in input_split[1:]:
                paramKey, paramValue = param.split('=')
                if Util.is_number(paramValue.strip()):
                    params[paramKey.strip()] = float(paramValue.strip())
                else:
                    params[paramKey.strip()] = paramValue.strip()
        except BaseException:
            return action, None

        return action, params

    @staticmethod
    def is_in_range(value, min_value, max_value, default_value, label=None):
        """
        Returns if the given value is within the given min and max; if not,
        returns the given default.

        Parameters
        ----------
        value : number
            The input value.
        min_value : number
            The min value.
        max_value : number
            The max value.
        default_value : number
            The default value.
        label : string
            A label for the input value.  If given, and if the input
            value is not within the range, will print an error.

        Returns
        -------
        number
        """
        if value > max_value or value < min_value:
            if label is not None:
                print(
                    'Value of ' +
                    label +
                    'needs to be between ' +
                    str(min_value) +
                    ' and ' +
                    str(max_value) +
                    '. Current value: ' +
                    str(value) +
                    '. Will be reset to ' +
                    str(default_value) +
                    '.')
            return default_value
        return value

    @staticmethod
    def is_number(value, label=None):
        """
        Returns if the given value is a number.

        Parameters
        ----------
        value :
            The input value.
        label : string
            A label for the input value.  If given, and if the
            input value is not a number, will print an error.

        Returns
        -------
        boolean
        """
        try:
            float(value)
            return True
        except ValueError:
            if label is not None:
                print(
                    'Value of ' +
                    label +
                    ' needs to be a number. Will be set to 0.')
            return False

    @staticmethod
    def value_to_str(input_value, depth=0):
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
        this_indent = " " * Util.NUMBER_OF_SPACES * depth
        next_indent = " " * Util.NUMBER_OF_SPACES * (depth + 1)
        if input_value is None:
            return "null"
        if isinstance(input_value, dict):
            text_list = []
            for dict_key, dict_value in input_value.items():
                text_list.append(
                    next_indent +
                    "\"" +
                    dict_key +
                    "\": " +
                    Util.value_to_str(
                        dict_value,
                        depth +
                        1))
            return "{}" if len(text_list) == 0 else "{\n" + \
                (",\n").join(text_list) + "\n" + this_indent + "}"
        if isinstance(input_value, (list, tuple, numpy.ndarray)):
            text_list = []
            for list_item in list(input_value):
                text_list.append(
                    next_indent +
                    Util.value_to_str(
                        list_item,
                        depth +
                        1))
            return "[]" if len(text_list) == 0 else "[\n" + \
                (",\n").join(text_list) + "\n" + this_indent + "]"
        if isinstance(input_value, bool):
            return "true" if input_value else "false"
        if isinstance(input_value, str):
            return "\"" + input_value.replace("\"", "\\\"") + "\""
        return str(input_value).replace("\n", "\n" + this_indent)

    @staticmethod
    def vector_to_string(vector):
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
        return (
            (
                '(' +
                str(vector['x']) +
                ',' +
                str(vector['y']) +
                ',' +
                str(vector['z']) +
                ')'
            )
            if vector is not None and
            'x' in vector and
            'y' in vector and
            'z' in vector
            else 'None'
        )

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
