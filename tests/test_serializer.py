import unittest

import numpy as np

import machine_common_sense as mcs


class TestSerializer(unittest.TestCase):

    @staticmethod
    def _helper_get_step_metadata():
        with open('tests/test.msgpack', 'rb') as file:
            packed_bytes = file.read()

        serializer = mcs.SerializerMsgPack()
        return serializer.deserialize(packed_bytes)

    def test_serialization_msgpack(self):
        unpacked_metadata = TestSerializer._helper_get_step_metadata()
        assert abs(unpacked_metadata.reward - (-0.036000000000000004)
                   ) < 1e-04, 'Reward unexpected.'
        assert abs(unpacked_metadata.rotation -
                   0.0) < 1e-04, 'Rotation unexpected.'
        assert isinstance(unpacked_metadata.object_list[-1].shape, str
                          ), 'Shape type unexpected.'

    def test_serialization_json(self):
        unpacked_metadata = TestSerializer._helper_get_step_metadata()

        serializer = mcs.SerializerJson()
        json_dump = serializer.serialize(unpacked_metadata)
        unpacked_metadata = serializer.deserialize(json_dump)
        self.assertEqual(len(unpacked_metadata.depth_map_list), 1)
        self.assertIsInstance(unpacked_metadata.depth_map_list[0], np.ndarray)
        self.assertEqual(unpacked_metadata.depth_map_list[0].shape, (400, 600))
        self.assertIsInstance(unpacked_metadata, mcs.StepMetadata)
        self.assertAlmostEqual(unpacked_metadata.reward, -0.036000000000000004)
        self.assertAlmostEqual(unpacked_metadata.rotation, 0.0, delta=1e-04)
        self.assertIsInstance(unpacked_metadata.object_list[-1].shape, str)
        self.assertIsInstance(
            unpacked_metadata.object_list[0].segment_color, dict)


if __name__ == '__main__':
    unittest.main()
