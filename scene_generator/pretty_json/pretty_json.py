from _ctypes import PyObj_FromPtr
import json
import re

# From
# https://stackoverflow.com/questions/13249415/how-to-implement-custom-indentation-when-pretty-printing-with-the-json-module


class PrettyJsonNoIndent(object):
    """ Value wrapper. """

    def __init__(self, value):
        self.value = value


class PrettyJsonEncoder(json.JSONEncoder):
    FORMAT_SPEC = '@@{}@@'
    regex = re.compile(FORMAT_SPEC.format(r'(\d+)'))

    def __init__(self, **kwargs):
        # Save copy of any keyword argument values needed for use here.
        self.__sort_keys = kwargs.get('sort_keys', None)
        super(PrettyJsonEncoder, self).__init__(**kwargs)

    def default(self, obj):
        return (
            self.FORMAT_SPEC.format(
                id(obj)) if isinstance(
                obj,
                PrettyJsonNoIndent) else super(
                PrettyJsonEncoder,
                self).default(obj))

    def encode(self, obj):
        format_spec = self.FORMAT_SPEC  # Local var to expedite access.
        json_repr = super(PrettyJsonEncoder, self).encode(obj)  # Default JSON.

        # Replace any marked-up object ids in the JSON repr with the
        # value returned from the json.dumps() of the corresponding
        # wrapped Python object.
        for match in self.regex.finditer(json_repr):
            # see https://stackoverflow.com/a/15012814/355230
            id = int(match.group(1))
            no_indent = PyObj_FromPtr(id)
            json_obj_repr = json.dumps(
                no_indent.value,
                cls=PrettyJsonEncoder,
                sort_keys=self.__sort_keys,
                separators=(
                    ',',
                    ':'))

            # Replace the matched id string with json formatted representation
            # of the corresponding Python object.
            json_repr = json_repr.replace(
                '"{}"'.format(
                    format_spec.format(id)),
                json_obj_repr)

        return json_repr
