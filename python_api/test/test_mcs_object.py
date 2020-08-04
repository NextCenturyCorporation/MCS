import unittest
import textwrap

from machine_common_sense.mcs_object import MCS_Object


class Test_Default_MCS_Object(unittest.TestCase):

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
        cls.mcs_object = MCS_Object()

    @classmethod
    def tearDownClass(cls):
        # nothing to do
        pass

    def test_uuid(self):
        self.assertEqual(self.mcs_object.uuid, "")
        self.assertIsInstance(self.mcs_object.uuid, str)

    def test_color(self):
        self.assertFalse(self.mcs_object.color)
        self.assertIsInstance(self.mcs_object.color, dict)

    def test_dimensions(self):
        self.assertFalse(self.mcs_object.dimensions)
        self.assertIsInstance(self.mcs_object.dimensions, dict)

    def test_direction(self):
        self.assertFalse(self.mcs_object.direction)
        self.assertIsInstance(self.mcs_object.direction, dict)

    def test_distance(self):
        self.assertAlmostEqual(self.mcs_object.distance, -1.0)
        self.assertIsInstance(self.mcs_object.distance, float)

    def test_distance_in_steps(self):
        self.assertAlmostEqual(self.mcs_object.distance_in_steps, -1.0)
        self.assertIsInstance(self.mcs_object.distance_in_steps, float)

    def test_distance_in_world(self):
        self.assertAlmostEqual(self.mcs_object.distance_in_world, -1.0)
        self.assertIsInstance(self.mcs_object.distance_in_world, float)

    def test_held(self):
        self.assertFalse(self.mcs_object.held)
        self.assertIsInstance(self.mcs_object.held, bool)

    def test_mass(self):
        self.assertAlmostEqual(self.mcs_object.mass, 0.0)
        self.assertIsInstance(self.mcs_object.mass, float)

    def test_material_list(self):
        self.assertFalse(self.mcs_object.material_list)
        self.assertIsInstance(self.mcs_object.material_list, list)

    def test_position(self):
        self.assertFalse(self.mcs_object.position)
        self.assertIsInstance(self.mcs_object.position, dict)

    def test_rotation(self):
        self.assertFalse(self.mcs_object.rotation)
        self.assertIsInstance(self.mcs_object.rotation, dict)

    def test_shape(self):
        self.assertEqual(self.mcs_object.shape, "")
        self.assertIsInstance(self.mcs_object.shape, str)

    def test_texture_color_list(self):
        self.assertFalse(self.mcs_object.texture_color_list)
        self.assertIsInstance(self.mcs_object.texture_color_list, list)

    def test_visible(self):
        self.assertIsInstance(self.mcs_object.visible, bool)
        self.assertFalse(self.mcs_object.visible)

    def test_str(self):
        self.assertEqual(str(self.mcs_object),
                         textwrap.dedent(self.str_output))
