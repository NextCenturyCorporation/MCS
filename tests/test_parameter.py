import unittest

from machine_common_sense.config_manager import ConfigManager
from machine_common_sense.controller import DEFAULT_MOVE
from machine_common_sense.parameter import Parameter


class TestParameter(unittest.TestCase):

    sc = {'screenshot': False,
          'version': 2,
          'floorTextures': [],
          'isometric': False,
          'performerStart': {'rotation': {'y': 0.0,
                                          'z': 0.0,
                                          'x': 0.0},
                             'position': {'y': 0.0,
                                          'z': 0.0,
                                          'x': 0.0}},
          'observation': False,
          'intuitivePhysics': False,
          'floorMaterial': 'AI2-THOR/Materials/Fabrics/CarpetWhite 3',
          'ceilingMaterial': 'AI2-THOR/Materials/Walls/Drywall',
          'holes': [],
          'objects': [{'shows': [{'position': {'y': 0.25,
                                               'z': 1.0,
                                               'x': 0.25},
                                  'boundingBox': [],
                                  'stepBegin': 0,
                                  'scale': {'y': 0.5,
                                            'z': 0.5,
                                            'x': 0.5},
                                  'rotation': {'y': 0.0,
                                               'z': 0.0,
                                               'x': 0.0}}],
                       'pickupable': False,
                       'mass': 1.0,
                       'materials': ['AI2-THOR/Materials/Plastics/BlueRubber'],
                       'salientMaterials': ['rubber'],
                       'moveable': False,
                       'type': 'ball',
                       'id': 'testBall1'},
                      {'shows': [{'position': {'y': 0.25,
                                               'z': 2.0,
                                               'x': -0.25},
                                  'boundingBox': [],
                                  'stepBegin': 0,
                                  'scale': {'y': 0.5,
                                            'z': 0.5,
                                            'x': 0.5},
                                  'rotation': {'y': 0.0,
                                               'z': 0.0,
                                               'x': 0.0}}],
                       'pickupable': False,
                       'mass': 1.0,
                       'materials': ['AI2-THOR/Materials/Plastics/BlueRubber'],
                       'salientMaterials': ['rubber'],
                       'moveable': False,
                       'type': 'ball',
                       'id': 'testBall2'}],
          'wallMaterial': 'AI2-THOR/Materials/Walls/Drywall',
          'name': 'depth and segmentation test',
          'roomDimensions': {'y': 3.0,
                             'z': 10.0,
                             'x': 10.0}}

    def setUp(self):
        config = ConfigManager(config_file_or_dict={})
        self.parameter_converter = Parameter(config)

    def test_initialization_wrap_step(self):
        wrapped_step = self.parameter_converter.wrap_step(
            action='Initialize', sceneConfig=self.sc)
        # sceneConfig does not get removed
        self.assertIsNotNone(wrapped_step.get('sceneConfig'))

    def test_initialization_build_ai2thor_step(self):
        wrapped_step, params = self.parameter_converter.build_ai2thor_step(
            action='Initialize', sceneConfig=self.sc)
        # sceneConfig gets removed
        self.assertIsNone(wrapped_step.get('sceneConfig'))

    def test_wrap_step_action(self):
        actual = self.parameter_converter.wrap_step(
            action="TestAction",
            numberProperty=1234,
            stringProperty="test_property")
        expected = {
            "action": "TestAction",
            "continuous": True,
            "gridSize": 0.1,
            "logs": True,
            "numberProperty": 1234,
            "renderDepthImage": False,
            "renderObjectImage": False,
            "snapToGrid": False,
            "stringProperty": "test_property",
            "consistentColors": False
        }
        self.assertEqual(actual, expected)

    def test_wrap_step_metadata_oracle(self):
        config = ConfigManager(config_file_or_dict={'metadata': 'oracle'})
        parameter_converter = Parameter(config)
        actual = parameter_converter.wrap_step(
            action="TestAction",
            numberProperty=1234,
            stringProperty="test_property")
        # Changed depth and object because oracle should result in both being
        # true.
        expected = {
            "action": "TestAction",
            "continuous": True,
            "gridSize": 0.1,
            "logs": True,
            "numberProperty": 1234,
            "renderDepthImage": True,
            "renderObjectImage": True,
            "snapToGrid": False,
            "stringProperty": "test_property",
            "consistentColors": True
        }
        self.assertEqual(actual, expected)

    def test_wrap_step_metadata_level2(self):
        config = ConfigManager(config_file_or_dict={'metadata': 'level2'})
        parameter_converter = Parameter(config)
        actual = parameter_converter.wrap_step(
            action="TestAction",
            numberProperty=1234,
            stringProperty="test_property")
        # Changed depth and object because oracle should result in both being
        # true.
        expected = {
            "action": "TestAction",
            "continuous": True,
            "gridSize": 0.1,
            "logs": True,
            "numberProperty": 1234,
            "renderDepthImage": True,
            "renderObjectImage": True,
            "snapToGrid": False,
            "stringProperty": "test_property",
            "consistentColors": False
        }
        self.assertEqual(actual, expected)

    def test_wrap_step_metadata_level1(self):
        config = ConfigManager(config_file_or_dict={'metadata': 'level1'})
        parameter_converter = Parameter(config)
        actual = parameter_converter.wrap_step(
            action="TestAction",
            numberProperty=1234,
            stringProperty="test_property")
        # Changed depth and object because oracle should result in both being
        # true.
        expected = {
            "action": "TestAction",
            "continuous": True,
            "gridSize": 0.1,
            "logs": True,
            "numberProperty": 1234,
            "renderDepthImage": True,
            "renderObjectImage": False,
            "snapToGrid": False,
            "stringProperty": "test_property",
            "consistentColors": False
        }
        self.assertEqual(actual, expected)

    def test_generate_noise(self):
        min_noise = self.parameter_converter.MIN_NOISE
        max_noise = self.parameter_converter.MAX_NOISE

        current_noise = self.parameter_converter._generate_noise()
        self.assertTrue(min_noise <= current_noise <= max_noise)

    def test_get_amount(self):
        amount = self.parameter_converter._get_amount(action="", amount=1)
        self.assertIsInstance(amount, float)
        self.assertAlmostEqual(amount, 1.0)

        amount = self.parameter_converter._get_amount()
        self.assertIsInstance(amount, float)
        self.assertAlmostEqual(amount, Parameter.DEFAULT_AMOUNT)

        amount = self.parameter_converter._get_amount(
            action=Parameter.OBJECT_MOVE_ACTIONS[0])
        self.assertIsInstance(amount, float)
        self.assertAlmostEqual(amount, Parameter.DEFAULT_OBJECT_MOVE_AMOUNT)

        amount = self.parameter_converter._get_amount(amount=None)
        self.assertIsInstance(amount, float)
        self.assertAlmostEqual(amount, Parameter.DEFAULT_AMOUNT)

        self.assertRaises(
            ValueError,
            lambda: self.parameter_converter._get_amount(amount="string")
        )

        self.assertRaises(
            ValueError,
            lambda: self.parameter_converter._get_amount(amount=1.1)
        )

        self.assertRaises(
            ValueError,
            lambda: self.parameter_converter._get_amount(amount=-0.1)
        )

    def test_get_force(self):
        force = self.parameter_converter._get_force(force=1)
        self.assertIsInstance(force, float)
        self.assertAlmostEqual(force, 1.0)

        force = self.parameter_converter._get_force()
        self.assertIsInstance(force, float)
        self.assertAlmostEqual(force, Parameter.DEFAULT_FORCE)

        force = self.parameter_converter._get_force(force=None)
        self.assertIsInstance(force, float)
        self.assertAlmostEqual(force, Parameter.DEFAULT_FORCE)

        self.assertRaises(
            ValueError,
            lambda: self.parameter_converter._get_force(force="string")
        )

        self.assertRaises(
            ValueError,
            lambda: self.parameter_converter._get_force(force=1.1)
        )

        self.assertRaises(
            ValueError,
            lambda: self.parameter_converter._get_force(force=-0.1)
        )

    def test_get_number(self):
        number = self.parameter_converter._get_number(key="val", val=7)
        self.assertEqual(number, 7)
        self.assertIsInstance(number, float)

        number = self.parameter_converter._get_number(key="val", not_val=7)
        self.assertIsNone(number)

        self.assertRaises(
            ValueError,
            lambda: self.parameter_converter._get_number(
                key="string", string="invalid"
            )
        )

    def test_get_number_with_default(self):
        number = self.parameter_converter._get_number_with_default(
            key="val", default=5, val=7)
        self.assertEqual(number, 7)
        self.assertIsInstance(number, float)

        number = self.parameter_converter._get_number_with_default(
            key="val", default=5, not_val=7)
        self.assertEqual(number, 5)
        self.assertIsInstance(number, float)

        self.assertRaises(
            ValueError,
            lambda: self.parameter_converter._get_number_with_default(
                key="string", default=5, string="invalid")
        )

        number = self.parameter_converter._get_number_with_default(
            key="val", default=5, val=None
        )
        self.assertEqual(number, 5)
        self.assertIsInstance(number, float)

    def test_get_move_magnitude(self):
        magnitude = self.parameter_converter._get_move_magnitude(
            action="",
            force=0.5,
            amount=0.7
        )
        self.assertIsInstance(magnitude, float)
        self.assertEqual(magnitude, DEFAULT_MOVE)

        magnitude = self.parameter_converter._get_move_magnitude(
            action=Parameter.FORCE_ACTIONS[0],
            force=0.5,
            amount=0.7
        )
        self.assertIsInstance(magnitude, float)
        self.assertEqual(magnitude, 0.5)

        magnitude = self.parameter_converter._get_move_magnitude(
            action=Parameter.OBJECT_MOVE_ACTIONS[0],
            force=0.5,
            amount=0.7
        )
        self.assertIsInstance(magnitude, float)
        self.assertEqual(magnitude, 0.7)

    def test_get_teleport(self):
        (teleport_rot, teleport_pos) = self.parameter_converter._get_teleport()
        self.assertIsNone(teleport_rot)
        self.assertIsNone(teleport_pos)

        (teleport_rot, teleport_pos) = self.parameter_converter._get_teleport(
            yRotation=90
        )
        self.assertEqual(teleport_rot, {'y': 90.0})
        self.assertIsNone(teleport_pos)

        (teleport_rot, teleport_pos) = self.parameter_converter._get_teleport(
            xPosition=1, zPosition=2)
        self.assertIsNone(teleport_rot)
        self.assertEqual(teleport_pos, {'x': 1.0, 'z': 2.0})

        (teleport_rot, teleport_pos) = self.parameter_converter._get_teleport(
            yRotation=90, xPosition=1, zPosition='2')
        self.assertEqual(teleport_rot, {'y': 90.0})
        self.assertEqual(teleport_pos, {'x': 1.0, 'z': 2.0})

        self.assertRaises(
            ValueError,
            lambda: self.parameter_converter._get_teleport(
                yRotation='invalid',
                xPosition='1',
                zPosition='2')
        )

        self.assertRaises(
            ValueError,
            lambda: self.parameter_converter._get_teleport(
                yRotation='90',
                xPosition='invalid',
                zPosition='2'
            )
        )

        self.assertRaises(
            ValueError,
            lambda: self.parameter_converter._get_teleport(
                yRotation=90,
                xPosition=1,
                zPosition='invalid'
            )
        )

    def test_teleport_position(self):
        position = self.parameter_converter._get_teleport_position(
            xPosition=1, zPosition=2)
        self.assertIsInstance(position, dict)
        self.assertIn('x', position)
        self.assertIn('z', position)
        self.assertIsInstance(position['x'], float)
        self.assertIsInstance(position['z'], float)
        self.assertEqual(position['x'], 1)
        self.assertEqual(position['z'], 2)

        position = self.parameter_converter._get_teleport_position(
            xPosition=None, zPosition=None)
        self.assertIsNone(position)

        position = self.parameter_converter._get_teleport_position(
            xPosition=None, zPosition=2)
        self.assertIsNone(position)

        position = self.parameter_converter._get_teleport_position(
            xPosition=1, zPosition=None)
        self.assertIsNone(position)

    def test_teleport_rotation(self):
        rotation = self.parameter_converter._get_teleport_rotation(
            yRotation=45)
        self.assertIsInstance(rotation, dict)
        self.assertIn('y', rotation)
        self.assertIsInstance(rotation['y'], float)
        self.assertEqual(rotation['y'], 45)

        rotation = self.parameter_converter._get_teleport_rotation(
            yRotation=None)
        self.assertIsNone(rotation)

    def test_convert_y_image_coord_for_unity(self):
        image_coord = 0
        unity_coord = \
            self.parameter_converter._convert_y_image_coord_for_unity(
                image_coord)
        screen_height = self.parameter_converter.config.get_screen_height()
        self.assertEqual(unity_coord, screen_height - 1)

        image_coord = screen_height - 1  # screen height is out of bounds
        unity_coord = \
            self.parameter_converter._convert_y_image_coord_for_unity(
                image_coord)
        self.assertEqual(unity_coord, 0)

        image_coord = screen_height
        self.assertRaises(
            ValueError,
            lambda: self.parameter_converter._convert_y_image_coord_for_unity(
                y_coord=image_coord
            )
        )

        # value much greater than the screen height
        image_coord = 1000000
        self.assertRaises(
            ValueError,
            lambda: self.parameter_converter._convert_y_image_coord_for_unity(
                y_coord=image_coord
            )
        )

        # value less than the origin
        image_coord = -1
        self.assertRaises(
            ValueError,
            lambda: self.parameter_converter._convert_y_image_coord_for_unity(
                y_coord=image_coord
            )
        )

        # Invalid image coordinate
        image_coord = None
        self.assertRaises(
            TypeError,
            lambda: self.parameter_converter._convert_y_image_coord_for_unity(
                y_coord=image_coord
            )
        )

        # Invalid image coordinate value
        image_coord = "one"
        self.assertRaises(
            TypeError,
            lambda: self.parameter_converter._convert_y_image_coord_for_unity(
                y_coord=image_coord
            )
        )

    def test_mcs_action_to_ai2thor_action(self):
        # TODO any string is passed through
        # should we leave an Action enum?
        ai2thor_action = \
            self.parameter_converter._mcs_action_to_ai2thor_action(
                "")
        self.assertIsInstance(ai2thor_action, str)
        self.assertEqual(ai2thor_action, "")

        ai2thor_action = \
            self.parameter_converter._mcs_action_to_ai2thor_action(
                "OpenObject")
        self.assertIsInstance(ai2thor_action, str)
        self.assertEqual(ai2thor_action, "MCSOpenObject")

        ai2thor_action = \
            self.parameter_converter._mcs_action_to_ai2thor_action(
                "CloseObject")
        self.assertIsInstance(ai2thor_action, str)
        self.assertEqual(ai2thor_action, "MCSCloseObject")

        ai2thor_action = \
            self.parameter_converter._mcs_action_to_ai2thor_action(
                "DropObject")
        self.assertIsInstance(ai2thor_action, str)
        self.assertEqual(ai2thor_action, "DropHandObject")
