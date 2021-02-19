import unittest
from machine_common_sense.serializer import *


class TestSerializer(unittest.TestCase):

    @staticmethod
    def _helper_get_step_metadata():
        with open('./test.msgpack', 'rb') as file:
            packed_bytes = file.read()

        serializer = SerializerMsgPack()
        return serializer.deserialize(packed_bytes)

    def test_serialization_msgpack(self):
        unpacked_metadata = TestSerializer._helper_get_step_metadata()
        assert unpacked_metadata.reward == 0.0, 'Reward unexpected.'
        assert unpacked_metadata.rotation == 0.0, 'Rotation unexpected.'

    def test_serialization_json(self):
        unpacked_metadata = TestSerializer._helper_get_step_metadata()

        serializer = SerializerJson()
        json_dump = serializer.serialize(unpacked_metadata)
        unpacked_metadata = serializer.deserialize(json_dump)
        self.assertEqual(len(unpacked_metadata.depth_map_list), 1)
        self.assertIsInstance(unpacked_metadata.depth_map_list[0], np.ndarray)
        self.assertEqual(unpacked_metadata.depth_map_list[0].shape, (400, 600))
        self.assertIsInstance(unpacked_metadata, StepMetadata)
        self.assertEqual(unpacked_metadata.reward, 0.0)
        self.assertEqual(unpacked_metadata.rotation, 0.0)


if __name__ == '__main__':
    unittest.main()
