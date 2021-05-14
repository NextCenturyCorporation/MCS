import unittest

import machine_common_sense as mcs


class MyEmptyclass:

    def __init__(self):
        pass


class MySubclass:

    def __init__(self):
        self.my_integer = 7
        self.my_string = "h"
        self.my_list = [8, "i"]
        self.my_dict = {
            "my_integer": 9,
            "my_string": "j",
        }

    def __str__(self):
        return mcs.Stringifier.class_to_str(self)


class MyClass:

    def __init__(self):
        self.my_boolean = True
        self.my_float = 1.234
        self.my_integer = 0
        self.my_string = "a"
        self.my_list = [1, "b", {
            "my_integer": 2,
            "my_string": "c",
            "my_list": [3, "d"]
        }]
        self.my_dict = {
            "my_integer": 4,
            "my_string": "e",
            "my_list": [5, "f"],
            "my_dict": {
                "my_integer": 6,
                "my_string": "g",
            }
        }
        self.my_list_empty = []
        self.my_dict_empty = {}
        self.my_subclass = MySubclass()
        self.__my_private = "z"

    def my_function():
        pass


class TestStringifier(unittest.TestCase):

    def test_class_to_str_with_class(self):
        self.maxDiff = 10000
        expected = "{\n    \"my_boolean\": true,\n    \"my_float\": 1.234,\n    \"my_integer\": 0,\n    \"my_string\": \"a\",\n    \"my_list\": [\n        1,\n        \"b\",\n        {\n            \"my_integer\": 2,\n            \"my_string\": \"c\",\n            \"my_list\": [3,\"d\"]\n        }\n    ],\n    \"my_dict\": {\n        \"my_integer\": 4,\n        \"my_string\": \"e\",\n        \"my_list\": [5,\"f\"],\n        \"my_dict\": {\n            \"my_integer\": 6,\n            \"my_string\": \"g\"\n        }\n    },\n    \"my_list_empty\": [],\n    \"my_dict_empty\": {},\n    \"my_subclass\": {\n        \"my_integer\": 7,\n        \"my_string\": \"h\",\n        \"my_list\": [8,\"i\"],\n        \"my_dict\": {\n            \"my_integer\": 9,\n            \"my_string\": \"j\"\n        }\n    }\n}"  # noqa: E501
        self.assertEqual(mcs.Stringifier.class_to_str(MyClass()), expected)

    def test_class_to_str_with_empty_class(self):
        self.assertEqual(mcs.Stringifier.class_to_str(MyEmptyclass()), "{}")

    def test_generate_pretty_object_output(self):
        object_list = [
            mcs.ObjectMetadata(
                uuid='id1',
                shape='',
                state_list=[],
                texture_color_list=[],
                held=True,
                visible=True,
                position=None,
                dimensions=None,
                distance_in_world=0,
                direction=None
            ),
            mcs.ObjectMetadata(
                uuid='really_long_id2',
                shape='sofa',
                state_list=['state1', 'state2'],
                texture_color_list=['black', 'white'],
                held=False,
                visible=False,
                position={
                    'x': 1,
                    'y': 2,
                    'z': 3
                },
                dimensions=[{
                    'x': 4,
                    'y': 5,
                    'z': 6
                }],
                distance_in_world=1234567890987654321,
                direction={
                    'x': 10000,
                    'y': 20000,
                    'z': 30000
                }
            )
        ]
        self.assertEqual(mcs.Stringifier.generate_pretty_object_output(
            object_list), [
            'OBJECT ID        SHAPE  COLORS        HELD   VISIBLE  STATE           POSITION (WORLD)  DISTANCE (WORLD)     DIRECTION (WORLD)    DIMENSIONS (WORLD)',  # noqa: E501
            'id1                                   True   True                     None              0                    None                 None              ',  # noqa: E501
            'really_long_id2  sofa   black, white  False  False    state1, state2  (1,2,3)           1234567890987654321  (10000,20000,30000)  [(4,5,6)]         '  # noqa: E501
        ])

    def test_value_to_str_with_boolean(self):
        self.assertEqual(mcs.Stringifier.value_to_str(True), "true")
        self.assertEqual(mcs.Stringifier.value_to_str(False), "false")

    def test_value_to_str_with_dict(self):
        self.assertEqual(mcs.Stringifier.value_to_str({}), "{}")
        self.assertEqual(mcs.Stringifier.value_to_str({
            "number": 1,
            "string": "a"
        }), "{\n    \"number\": 1,\n    \"string\": \"a\"\n}")

    def test_value_to_str_with_float(self):
        self.assertEqual(mcs.Stringifier.value_to_str(0.0), "0.0")
        self.assertEqual(mcs.Stringifier.value_to_str(1234.5678), "1234.5678")
        self.assertEqual(mcs.Stringifier.value_to_str(0.12345678), "0.1235")
        self.assertEqual(mcs.Stringifier.value_to_str(-0.12345678), "-0.1235")

    def test_value_to_str_with_integer(self):
        self.assertEqual(mcs.Stringifier.value_to_str(0), "0")
        self.assertEqual(mcs.Stringifier.value_to_str(1234), "1234")

    def test_value_to_str_with_list(self):
        self.assertEqual(mcs.Stringifier.value_to_str([]), "[]")
        self.assertEqual(mcs.Stringifier.value_to_str([1, "a"]), "[1,\"a\"]")

    def test_value_to_str_with_list_with_nested_dict(self):
        self.assertEqual(mcs.Stringifier.value_to_str([]), "[]")
        self.assertEqual(
            mcs.Stringifier.value_to_str([1, "a", {"b": 2}]),
            "[\n    1,\n    \"a\",\n    {\n        \"b\": 2\n    }\n]"
        )

    def test_value_to_str_with_list_with_nested_list(self):
        self.assertEqual(mcs.Stringifier.value_to_str([]), "[]")
        self.assertEqual(
            mcs.Stringifier.value_to_str([1, "a", [2, "b"]]),
            "[\n    1,\n    \"a\",\n    [2,\"b\"]\n]"
        )

    def test_value_to_str_with_string(self):
        self.assertEqual(mcs.Stringifier.value_to_str(""), "\"\"")
        self.assertEqual(
            mcs.Stringifier.value_to_str("a b c d"),
            "\"a b c d\"")

    def test_vector_to_string(self):
        self.assertEqual(mcs.Stringifier.vector_to_string(None), 'None')
        self.assertEqual(mcs.Stringifier.vector_to_string({
            'x': 1,
            'y': 2,
            'z': 3
        }), '(1,2,3)')


if __name__ == '__main__':
    unittest.main()
