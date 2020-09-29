import unittest

import machine_common_sense as mcs


class My_Emptyclass:

    def __init__(self):
        pass


class My_Subclass:

    def __init__(self):
        self.my_integer = 7
        self.my_string = "h"
        self.my_list = [8, "i"]
        self.my_dict = {
            "my_integer": 9,
            "my_string": "j",
        }

    def __str__(self):
        return mcs.Util.class_to_str(self)


class My_Class:

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
        self.my_subclass = My_Subclass()
        self.__my_private = "z"

    def my_function():
        pass


class Test_Util(unittest.TestCase):

    def test_class_to_str_with_class(self):
        self.maxDiff = 10000
        expected = "{\n    \"my_boolean\": true,\n    \"my_float\": 1.234,\n    \"my_integer\": 0,\n    \"my_string\": \"a\",\n    \"my_list\": [\n        1,\n        \"b\",\n        {\n            \"my_integer\": 2,\n            \"my_string\": \"c\",\n            \"my_list\": [\n                3,\n                \"d\"\n            ]\n        }\n    ],\n    \"my_dict\": {\n        \"my_integer\": 4,\n        \"my_string\": \"e\",\n        \"my_list\": [\n            5,\n            \"f\"\n        ],\n        \"my_dict\": {\n            \"my_integer\": 6,\n            \"my_string\": \"g\"\n        }\n    },\n    \"my_list_empty\": [],\n    \"my_dict_empty\": {},\n    \"my_subclass\": {\n        \"my_integer\": 7,\n        \"my_string\": \"h\",\n        \"my_list\": [\n            8,\n            \"i\"\n        ],\n        \"my_dict\": {\n            \"my_integer\": 9,\n            \"my_string\": \"j\"\n        }\n    }\n}"  # noqa: E501
        self.assertEqual(mcs.Util.class_to_str(My_Class()), expected)

    def test_class_to_str_with_empty_class(self):
        self.assertEqual(mcs.Util.class_to_str(My_Emptyclass()), "{}")

    def test_generate_pretty_object_output(self):
        object_list = [
            mcs.ObjectMetadata(
                uuid='id1',
                shape='',
                texture_color_list=[],
                held=True,
                position=None,
                dimensions=None,
                distance_in_world=0,
                direction=None
            ),
            mcs.ObjectMetadata(
                uuid='really_long_id2',
                shape='sofa',
                texture_color_list=['black', 'white'],
                held=False,
                position={
                    'x': 1,
                    'y': 2,
                    'z': 3
                },
                dimensions={
                    'x': 4,
                    'y': 5,
                    'z': 6
                },
                distance_in_world=1234567890987654321,
                direction={
                    'x': 10000,
                    'y': 20000,
                    'z': 30000
                }
            )
        ]
        self.assertEqual(mcs.Util.generate_pretty_object_output(object_list), [
            'OBJECT ID        SHAPE  COLORS        HELD   POSITION (WORLD)  DIMENSIONS (WORLD)  DISTANCE (WORLD)     DIRECTION (WORLD)  ',  # noqa: E501
            'id1                                   True   None              None                0                    None               ',  # noqa: E501
            'really_long_id2  sofa   black, white  False  (1,2,3)           (4,5,6)             1234567890987654321  (10000,20000,30000)'  # noqa: E501
        ])

    def test_input_to_action_and_params(self):
        self.assertEqual(mcs.Util.input_to_action_and_params(
            'MoveBack'), ('MoveBack', {}))
        self.assertEqual(mcs.Util.input_to_action_and_params(
            'RotateLook,rotation=12.34'), ('RotateLook', {'rotation': 12.34}))
        self.assertEqual(
            mcs.Util.input_to_action_and_params(
                'PickupObject,objectId=testId'
            ),
            ('PickupObject', {'objectId': 'testId'})
        )
        self.assertEqual(
            mcs.Util.input_to_action_and_params(
                'PushObject,objectId=testId,force=12.34'
            ),
            ('PushObject', {'objectId': 'testId', 'force': 12.34})
        )
        self.assertEqual(
            mcs.Util.input_to_action_and_params('Foobar'), (None, {}))
        self.assertEqual(mcs.Util.input_to_action_and_params(
            'MoveBack,key:value'), ('MoveBack', None))

    def test_is_in_range(self):
        self.assertEqual(mcs.Util.is_in_range(0, 0, 1, 1234), 0)
        self.assertEqual(mcs.Util.is_in_range(0.5, 0, 1, 1234), 0.5)
        self.assertEqual(mcs.Util.is_in_range(1, 0, 1, 1234), 1)

        self.assertEqual(mcs.Util.is_in_range(-1, 0, 1, 1234), 1234)
        self.assertEqual(mcs.Util.is_in_range(1.01, 0, 1, 1234), 1234)
        self.assertEqual(mcs.Util.is_in_range(100, 0, 1, 1234), 1234)

        self.assertEqual(mcs.Util.is_in_range(2, 2, 4, 1234), 2)
        self.assertEqual(mcs.Util.is_in_range(2.1, 2, 4, 1234), 2.1)
        self.assertEqual(mcs.Util.is_in_range(4, 2, 4, 1234), 4)

        self.assertEqual(mcs.Util.is_in_range(1.9, 2, 4, 1234), 1234)
        self.assertEqual(mcs.Util.is_in_range(-3, 2, 4, 1234), 1234)
        self.assertEqual(mcs.Util.is_in_range(4.1, 2, 4, 1234), 1234)

        self.assertEqual(mcs.Util.is_in_range(-2, -2, 2, 1234), -2)
        self.assertEqual(mcs.Util.is_in_range(0, -2, 2, 1234), 0)
        self.assertEqual(mcs.Util.is_in_range(2, -2, 2, 1234), 2)

        self.assertEqual(mcs.Util.is_in_range(-2.1, -2, 2, 1234), 1234)
        self.assertEqual(mcs.Util.is_in_range(2.1, -2, 2, 1234), 1234)
        self.assertEqual(mcs.Util.is_in_range(200, -2, 2, 1234), 1234)

        self.assertEqual(mcs.Util.is_in_range(-4, -4, -2, 1234), -4)
        self.assertEqual(mcs.Util.is_in_range(-2.1, -4, -2, 1234), -2.1)
        self.assertEqual(mcs.Util.is_in_range(-2, -4, -2, 1234), -2)

        self.assertEqual(mcs.Util.is_in_range(-5, -4, -2, 1234), 1234)
        self.assertEqual(mcs.Util.is_in_range(-1, -4, -2, 1234), 1234)
        self.assertEqual(mcs.Util.is_in_range(3, -4, -2, 1234), 1234)

    def test_is_number(self):
        self.assertEqual(mcs.Util.is_number('0'), True)
        self.assertEqual(mcs.Util.is_number('1'), True)
        self.assertEqual(mcs.Util.is_number('12.34'), True)
        self.assertEqual(mcs.Util.is_number('01'), True)
        self.assertEqual(mcs.Util.is_number(''), False)
        self.assertEqual(mcs.Util.is_number('asdf'), False)

    def test_value_to_str_with_boolean(self):
        self.assertEqual(mcs.Util.value_to_str(True), "true")
        self.assertEqual(mcs.Util.value_to_str(False), "false")

    def test_value_to_str_with_dict(self):
        self.assertEqual(mcs.Util.value_to_str({}), "{}")
        self.assertEqual(mcs.Util.value_to_str({
            "number": 1,
            "string": "a"
        }), "{\n    \"number\": 1,\n    \"string\": \"a\"\n}")

    def test_value_to_str_with_float(self):
        self.assertEqual(mcs.Util.value_to_str(0.0), "0.0")
        self.assertEqual(mcs.Util.value_to_str(1234.5678), "1234.5678")

    def test_value_to_str_with_integer(self):
        self.assertEqual(mcs.Util.value_to_str(0), "0")
        self.assertEqual(mcs.Util.value_to_str(1234), "1234")

    def test_value_to_str_with_list(self):
        self.assertEqual(mcs.Util.value_to_str([]), "[]")
        self.assertEqual(mcs.Util.value_to_str(
            [1, "a"]), "[\n    1,\n    \"a\"\n]")

    def test_value_to_str_with_string(self):
        self.assertEqual(mcs.Util.value_to_str(""), "\"\"")
        self.assertEqual(mcs.Util.value_to_str("a b c d"), "\"a b c d\"")

    def test_vector_to_string(self):
        self.assertEqual(mcs.Util.vector_to_string(None), 'None')
        self.assertEqual(mcs.Util.vector_to_string({
            'x': 1,
            'y': 2,
            'z': 3
        }), '(1,2,3)')

    def test_verify_material_enum_string(self):
        self.assertEqual(mcs.Util.verify_material_enum_string('Ceramic'), True)
        self.assertEqual(mcs.Util.verify_material_enum_string('Plastic'), True)
        self.assertEqual(mcs.Util.verify_material_enum_string('Foobar'), False)
        self.assertEqual(mcs.Util.verify_material_enum_string(''), False)
