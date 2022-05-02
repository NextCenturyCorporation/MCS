import logging

import numpy

logger = logging.getLogger(__name__)


class Stringifier:
    """
    Defines functions to turn objects into strings for debugging and
    human readable output.  It is not intended to be reconstructed
    which is why this is seperate from serialization
    """

    NUMBER_OF_DECIMALS = 6
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
        this_indent = " " * Stringifier.NUMBER_OF_SPACES * depth
        next_indent = " " * Stringifier.NUMBER_OF_SPACES * (depth + 1)
        props = {
            prop_key: prop_value
            for prop_key, prop_value in vars(input_class).items()
            if not prop_key.startswith('_') or callable(prop_value)
        }
        text_list = [next_indent +
                     "\"" +
                     prop_key +
                     "\": " +
                     Stringifier.value_to_str(
                         prop_value,
                         depth +
                         1) for prop_key, prop_value in props.items()]
        return "{}" if not text_list else "{\n" + \
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
            "VISIBLE",
            "STATE",
            "POSITION (WORLD)",
            "DISTANCE (WORLD)",
            "DIRECTION (WORLD)",
            "DIMENSIONS (WORLD)"
        ]
        rows = [titles] + [
            [
                metadata.uuid,
                metadata.shape,
                ", ".join(metadata.texture_color_list)
                if (metadata.texture_color_list is not None)
                else metadata.texture_color_list,
                metadata.held,
                metadata.visible,
                ", ".join(metadata.state_list)
                if (metadata.state_list is not None)
                else metadata.state_list,
                Stringifier.vector_to_string(metadata.position),
                metadata.distance_in_world,
                Stringifier.vector_to_string(metadata.direction),
                (
                    (
                        "[" +
                        ", ".join(
                            Stringifier.vector_to_string(corner)
                            for corner in metadata.dimensions
                        )
                    ) +
                    "]"
                )
                if metadata.dimensions
                else None,
            ]
            for metadata in object_list
        ]

        widths = [max(len(str(row[i])) for row in rows)
                  for i in range(len(titles))]
        return [
            "  ".join(str(row[i]).ljust(widths[i]) for i in range(len(row)))
            for row in rows
        ]

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
        this_indent = " " * Stringifier.NUMBER_OF_SPACES * depth
        next_indent = " " * Stringifier.NUMBER_OF_SPACES * (depth + 1)
        if input_value is None:
            return "null"
        if isinstance(input_value, dict):
            text_list = [
                next_indent + "\"" + str(dict_key) + "\": " +
                Stringifier.value_to_str(dict_value, depth + 1)
                for dict_key, dict_value in input_value.items()
            ]
            return "{}" if not text_list else "{\n" + \
                (",\n").join(text_list) + "\n" + this_indent + "}"
        if isinstance(input_value, (list, tuple, numpy.ndarray)):
            input_value_as_list = list(input_value)
            condense = not any(
                isinstance(list_item, (dict, list, tuple, numpy.ndarray))
                for list_item in input_value_as_list
            )

            if condense:
                # To condense the list output, remove all of the whitespace.
                text_list = [
                    Stringifier.value_to_str(list_item, 0)
                    for list_item in input_value_as_list
                ]
                return "[" + (",").join(text_list) + "]"
            # Else the list output will separate list elements with newlines.
            text_list = [
                next_indent + Stringifier.value_to_str(list_item, depth + 1)
                for list_item in input_value_as_list
            ]
            return "[]" if not text_list else "[\n" + \
                (",\n").join(text_list) + "\n" + this_indent + "]"
        if isinstance(input_value, bool):
            return "true" if input_value else "false"
        if isinstance(input_value, (float, numpy.float32, numpy.float64)):
            return str(round(input_value, Stringifier.NUMBER_OF_DECIMALS))
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
                '(' + str(round(vector['x'], Stringifier.NUMBER_OF_DECIMALS)) +
                ',' + str(round(vector['y'], Stringifier.NUMBER_OF_DECIMALS)) +
                ',' + str(round(vector['z'],
                                Stringifier.NUMBER_OF_DECIMALS)) + ')'
            )
            if vector is not None and 'x' in vector and 'y' in vector and
            'z' in vector else 'None'
        )
