import unittest

import machine_common_sense as mcs


class TestMaterial(unittest.TestCase):
    def test_verify_material_enum_string(self):
        self.assertEqual(
            mcs.Material.verify_material_enum_string('Ceramic'), True)
        self.assertEqual(
            mcs.Material.verify_material_enum_string('Plastic'), True)
        self.assertEqual(
            mcs.Material.verify_material_enum_string('Foobar'), False)
        self.assertEqual(mcs.Material.verify_material_enum_string(''), False)


if __name__ == '__main__':
    unittest.main()
