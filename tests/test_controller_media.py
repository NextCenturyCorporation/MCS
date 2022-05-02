import unittest

import numpy as np
from numpy.testing import assert_array_equal

from machine_common_sense.controller_media import convert_depth_to_hsv


class TestControllerMedia(unittest.TestCase):

    def test_convert_depth_to_hsv_hue(self):
        diff = 0.375 / 256.0
        input_array = np.array([np.arange(0, 0.375, diff)])
        actual_output = convert_depth_to_hsv(input_array, 150.0)
        expected_output = np.array([[[i, 55, 255] for i in range(0, 256)]])
        assert_array_equal(actual_output, expected_output)

    def test_convert_depth_to_hsv_sat_and_val(self):
        input_array = np.array([
            np.arange(i, i + 3.75, 0.375) for i in np.arange(0, 150, 3.75)
        ])
        actual_output = convert_depth_to_hsv(input_array, 150.0)
        expected_output = np.reshape(np.array([
            [[0, i, 255] for i in range(55, 256)] +
            [[0, 255, i] for i in reversed(range(56, 255))]
        ]), (40, 10, 3))
        assert_array_equal(actual_output, expected_output)


if __name__ == '__main__':
    unittest.main()
