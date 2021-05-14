import unittest

import machine_common_sense as mcs


class TestValidation(unittest.TestCase):

    def test_is_in_range(self):
        self.assertEqual(mcs.Validation.is_in_range(0, 0, 1, 1234), 0)
        self.assertEqual(mcs.Validation.is_in_range(0.5, 0, 1, 1234), 0.5)
        self.assertEqual(mcs.Validation.is_in_range(1, 0, 1, 1234), 1)

        self.assertEqual(mcs.Validation.is_in_range(-1, 0, 1, 1234), 1234)
        self.assertEqual(mcs.Validation.is_in_range(1.01, 0, 1, 1234), 1234)
        self.assertEqual(mcs.Validation.is_in_range(100, 0, 1, 1234), 1234)

        self.assertEqual(mcs.Validation.is_in_range(2, 2, 4, 1234), 2)
        self.assertEqual(mcs.Validation.is_in_range(2.1, 2, 4, 1234), 2.1)
        self.assertEqual(mcs.Validation.is_in_range(4, 2, 4, 1234), 4)

        self.assertEqual(mcs.Validation.is_in_range(1.9, 2, 4, 1234), 1234)
        self.assertEqual(mcs.Validation.is_in_range(-3, 2, 4, 1234), 1234)
        self.assertEqual(mcs.Validation.is_in_range(4.1, 2, 4, 1234), 1234)

        self.assertEqual(mcs.Validation.is_in_range(-2, -2, 2, 1234), -2)
        self.assertEqual(mcs.Validation.is_in_range(0, -2, 2, 1234), 0)
        self.assertEqual(mcs.Validation.is_in_range(2, -2, 2, 1234), 2)

        self.assertEqual(mcs.Validation.is_in_range(-2.1, -2, 2, 1234), 1234)
        self.assertEqual(mcs.Validation.is_in_range(2.1, -2, 2, 1234), 1234)
        self.assertEqual(mcs.Validation.is_in_range(200, -2, 2, 1234), 1234)

        self.assertEqual(mcs.Validation.is_in_range(-4, -4, -2, 1234), -4)
        self.assertEqual(mcs.Validation.is_in_range(-2.1, -4, -2, 1234), -2.1)
        self.assertEqual(mcs.Validation.is_in_range(-2, -4, -2, 1234), -2)

        self.assertEqual(mcs.Validation.is_in_range(-5, -4, -2, 1234), 1234)
        self.assertEqual(mcs.Validation.is_in_range(-1, -4, -2, 1234), 1234)
        self.assertEqual(mcs.Validation.is_in_range(3, -4, -2, 1234), 1234)

    def test_is_number(self):
        self.assertEqual(mcs.Validation.is_number('0'), True)
        self.assertEqual(mcs.Validation.is_number('1'), True)
        self.assertEqual(mcs.Validation.is_number('12.34'), True)
        self.assertEqual(mcs.Validation.is_number('01'), True)
        self.assertEqual(mcs.Validation.is_number(''), False)
        self.assertEqual(mcs.Validation.is_number('asdf'), False)


if __name__ == '__main__':
    unittest.main()
