import unittest
import textwrap

import machine_common_sense as mcs


class TestObject(unittest.TestCase):

    str_output = '''    {
        "uuid": "",
        "color": {},
        "dimensions": {},
        "direction": {},
        "distance": -1.0,
        "distance_in_steps": -1.0,
        "distance_in_world": -1.0,
        "held": false,
        "mass": 0.0,
        "material_list": [],
        "position": {},
        "rotation": {},
        "shape": "",
        "texture_color_list": [],
        "visible": false
    }'''

    @classmethod
    def setUpClass(cls):
        cls.object = mcs.Object()

    @classmethod
    def tearDownClass(cls):
        # nothing to do
        pass

    def test_uuid(self):
        self.assertEqual(self.object.uuid, "")
        self.assertIsInstance(self.object.uuid, str)

    def test_color(self):
        self.assertFalse(self.object.color)
        self.assertIsInstance(self.object.color, dict)

    def test_dimensions(self):
        self.assertFalse(self.object.dimensions)
        self.assertIsInstance(self.object.dimensions, dict)

    def test_direction(self):
        self.assertFalse(self.object.direction)
        self.assertIsInstance(self.object.direction, dict)

    def test_distance(self):
        self.assertAlmostEqual(self.object.distance, -1.0)
        self.assertIsInstance(self.object.distance, float)

    def test_distance_in_steps(self):
        self.assertAlmostEqual(self.object.distance_in_steps, -1.0)
        self.assertIsInstance(self.object.distance_in_steps, float)

    def test_distance_in_world(self):
        self.assertAlmostEqual(self.object.distance_in_world, -1.0)
        self.assertIsInstance(self.object.distance_in_world, float)

    def test_held(self):
        self.assertFalse(self.object.held)
        self.assertIsInstance(self.object.held, bool)

    def test_mass(self):
        self.assertAlmostEqual(self.object.mass, 0.0)
        self.assertIsInstance(self.object.mass, float)

    def test_material_list(self):
        self.assertFalse(self.object.material_list)
        self.assertIsInstance(self.object.material_list, list)

    def test_position(self):
        self.assertFalse(self.object.position)
        self.assertIsInstance(self.object.position, dict)

    def test_rotation(self):
        self.assertFalse(self.object.rotation)
        self.assertIsInstance(self.object.rotation, dict)

    def test_shape(self):
        self.assertEqual(self.object.shape, "")
        self.assertIsInstance(self.object.shape, str)

    def test_texture_color_list(self):
        self.assertFalse(self.object.texture_color_list)
        self.assertIsInstance(self.object.texture_color_list, list)

    def test_visible(self):
        self.assertIsInstance(self.object.visible, bool)
        self.assertFalse(self.object.visible)

    def test_str(self):
        self.assertEqual(str(self.object),
                         textwrap.dedent(self.str_output))
