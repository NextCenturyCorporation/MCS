import textwrap
import unittest

import machine_common_sense as mcs


class TestObjectMetadata(unittest.TestCase):

    str_output = '''    {
        "uuid": "",
        "dimensions": [],
        "direction": {},
        "distance": -1.0,
        "distance_in_steps": -1.0,
        "distance_in_world": -1.0,
        "held": false,
        "mass": 0.0,
        "material_list": [],
        "position": {},
        "rotation": {},
        "segment_color": {},
        "shape": "",
        "state_list": [],
        "texture_color_list": [],
        "visible": false,
        "is_open": false,
        "openable": false
    }'''

    @classmethod
    def setUpClass(cls):
        cls.object_metadata = mcs.ObjectMetadata()

    @classmethod
    def tearDownClass(cls):
        # nothing to do
        pass

    def test_uuid(self):
        self.assertEqual(self.object_metadata.uuid, "")
        self.assertIsInstance(self.object_metadata.uuid, str)

    def test_dimensions(self):
        self.assertFalse(self.object_metadata.dimensions)
        self.assertIsInstance(self.object_metadata.dimensions, list)

    def test_direction(self):
        self.assertFalse(self.object_metadata.direction)
        self.assertIsInstance(self.object_metadata.direction, dict)

    def test_distance(self):
        self.assertAlmostEqual(self.object_metadata.distance, -1.0)
        self.assertIsInstance(self.object_metadata.distance, float)

    def test_distance_in_steps(self):
        self.assertAlmostEqual(self.object_metadata.distance_in_steps, -1.0)
        self.assertIsInstance(self.object_metadata.distance_in_steps, float)

    def test_distance_in_world(self):
        self.assertAlmostEqual(self.object_metadata.distance_in_world, -1.0)
        self.assertIsInstance(self.object_metadata.distance_in_world, float)

    def test_held(self):
        self.assertFalse(self.object_metadata.held)
        self.assertIsInstance(self.object_metadata.held, bool)

    def test_mass(self):
        self.assertAlmostEqual(self.object_metadata.mass, 0.0)
        self.assertIsInstance(self.object_metadata.mass, float)

    def test_material_list(self):
        self.assertFalse(self.object_metadata.material_list)
        self.assertIsInstance(self.object_metadata.material_list, list)

    def test_position(self):
        self.assertFalse(self.object_metadata.position)
        self.assertIsInstance(self.object_metadata.position, dict)

    def test_rotation(self):
        self.assertFalse(self.object_metadata.rotation)
        self.assertIsInstance(self.object_metadata.rotation, dict)

    def test_segment_color(self):
        self.assertFalse(self.object_metadata.segment_color)
        self.assertIsInstance(self.object_metadata.segment_color, dict)

    def test_shape(self):
        self.assertEqual(self.object_metadata.shape, "")
        self.assertIsInstance(self.object_metadata.shape, str)

    def test_state_list(self):
        self.assertFalse(self.object_metadata.state_list)
        self.assertIsInstance(self.object_metadata.state_list, list)

    def test_texture_color_list(self):
        self.assertFalse(self.object_metadata.texture_color_list)
        self.assertIsInstance(self.object_metadata.texture_color_list, list)

    def test_visible(self):
        self.assertIsInstance(self.object_metadata.visible, bool)
        self.assertFalse(self.object_metadata.visible)

    def test_str(self):
        self.assertEqual(str(self.object_metadata),
                         textwrap.dedent(self.str_output))


if __name__ == '__main__':
    unittest.main()
