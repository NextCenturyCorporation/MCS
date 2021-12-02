import unittest
from unittest.case import skip

import numpy as np
import PIL

import machine_common_sense as mcs
from machine_common_sense.goal_metadata import GoalMetadata
from machine_common_sense.object_metadata import ObjectMetadata
from machine_common_sense.serializer import (ISerializer, SerializerJson,
                                             SerializerMsgPack)
from machine_common_sense.step_metadata import StepMetadata


class TestISerializer(unittest.TestCase):

    def test_version(self):
        version = "0.1.0"
        self.assertEqual(ISerializer.version(), version)

    def test_serialize(self):
        self.assertRaises(NotImplementedError, ISerializer.serialize, None)

    def test_deserialize(self):
        self.assertRaises(NotImplementedError, ISerializer.deserialize, None)

    def test_image_to_bytes(self):
        size = (50, 100)
        black = (0, 0, 0)
        img = PIL.Image.new("RGB", size=size, color=black)
        image_bytes = ISerializer.image_to_bytes(img)
        self.assertIsInstance(image_bytes, bytes)
        image_str = image_bytes.decode('ISO-8859-1')
        self.assertTrue("PNG" in image_str)
        self.assertTrue("IHDR" in image_str)
        self.assertTrue("IDAT" in image_str)
        self.assertTrue("IEND" in image_str)

    def test_bytes_to_image(self):
        # bytes representing a black (0,0,0) 50x100 image
        image_bytes = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x002\x00' \
            b'\x00\x00d\x08\x02\x00\x00\x00K\x8a\xf4\x0c\x00\x00\x00' \
            b'&IDATx\x9c\xed\xc11\x01\x00\x00\x00\xc2\xa0\xf5Om\r\x0f' \
            b'\xa0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' \
            b'\x00\x00\xe0\xc3\x00:\xfc\x00\x01\xc0gM\x95\x00\x00\x00' \
            b'\x00IEND\xaeB`\x82'
        image = ISerializer.bytes_to_image(image_bytes)
        self.assertIsInstance(image, PIL.Image.Image)
        self.assertEqual(image.size, (50, 100))
        self.assertTrue(all(pixel == (0, 0, 0) for pixel in image.getdata()))


class TestSerializerMsgPack(unittest.TestCase):

    # allow larger unit tests comparisons for large dictionaries
    maxDiff = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.serializer = SerializerMsgPack()

    @classmethod
    def tearDownClass(cls) -> None:
        return super().tearDownClass()

    def test_serialize(self):
        packed_bytes = self.serializer.serialize(StepMetadata())
        self.assertIsInstance(packed_bytes, bytes)

    def test_deserializer(self):  # sourcery skip: class-extract-method
        # serialize a default StepMetadata()
        step_metadata = StepMetadata()
        packed_bytes = self.serializer.serialize(step_metadata)
        self.assertIsInstance(packed_bytes, bytes)

        # deserialize bytes back to a StepMetadata
        unpacked_step_metadata = self.serializer.deserialize(packed_bytes)
        self.assertIsInstance(unpacked_step_metadata, StepMetadata)

        # compare the two default StepMetadata objects
        self.assertEqual(
            unpacked_step_metadata.goal.__dict__,
            step_metadata.goal.__dict__)
        del step_metadata.goal
        del unpacked_step_metadata.goal
        self.assertEqual(
            unpacked_step_metadata.__dict__,
            step_metadata.__dict__)

    def test_ext_pack_with_stepmetadata(self):
        step_metadata = StepMetadata()
        step_exttype = self.serializer._ext_pack(step_metadata)
        self.assertEqual(step_exttype.code, 1)
        self.assertIsInstance(step_exttype.data, bytes)

    def test_ext_pack_with_tuple(self):
        test_tuple = (1, 'a')
        tuple_exttype = self.serializer._ext_pack(test_tuple)
        self.assertEqual(tuple_exttype.code, 2)
        self.assertIsInstance(tuple_exttype.data, bytes)
        self.assertEqual(tuple_exttype.data, b'\x92\x01\xa1a')

    def test_ext_pack_with_image(self):
        size = (50, 100)
        black = (0, 0, 0)
        img = PIL.Image.new("RGB", size=size, color=black)
        image_exttype = self.serializer._ext_pack(img)
        self.assertEqual(image_exttype.code, 3)
        self.assertIsInstance(image_exttype.data, bytes)
        image_str = image_exttype.data.decode('ISO-8859-1')
        self.assertTrue("PNG" in image_str)
        self.assertTrue("IHDR" in image_str)
        self.assertTrue("IDAT" in image_str)
        self.assertTrue("IEND" in image_str)

    def test_ext_pack_with_goalmetadata(self):
        goal_md = GoalMetadata()
        goal_exttype = self.serializer._ext_pack(goal_md)
        self.assertEqual(goal_exttype.code, 4)
        self.assertIsInstance(goal_exttype.data, bytes)

    def test_ext_pack_with_objectmetadata(self):
        obj_md = ObjectMetadata()
        obj_exttype = self.serializer._ext_pack(obj_md)
        self.assertEqual(obj_exttype.code, 5)
        self.assertIsInstance(obj_exttype.data, bytes)

    def test_ext_pack_with_ndarray(self):
        array = np.zeros(10)
        np_exttype = self.serializer._ext_pack(array)
        self.assertEqual(np_exttype.code, 6)
        self.assertIsInstance(np_exttype.data, bytes)

    def test_ext_unpack_with_stepmetadata(self):
        # from default StepMetadata()
        test_data = b'\xdc\x00\x12\x90\xc7\x13\x02\x92\xcb\x00\x00\x00\x00' \
            b'\x00\x00\x00\x00\xcb\x00\x00\x00\x00\x00\x00\x00\x00\xc7\x13' \
            b'\x02\x92\xcb\x00\x00\x00\x00\x00\x00\x00\x00\xcb\x00\x00\x00' \
            b'\x00\x00\x00\x00\x00\xcb\x00\x00\x00\x00\x00\x00\x00\x00\xcb' \
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x90\xd7\x04\x97\xc0\xa0\xa0' \
            b'\x00\x00\xc0\x80\xcb\x00\x00\x00\x00\x00\x00\x00\x00\x90\x90' \
            b'\x90\xa9UNDEFINED\x80\xa9UNDEFINED\x00\xcb\x00\x00\x00\x00' \
            b'\x00\x00\x00\x00\x00\x90'
        unpacked_step = self.serializer._ext_unpack(code=1, data=test_data)
        self.assertIsInstance(unpacked_step, StepMetadata)
        step_metadata = StepMetadata()
        # Removing default goal metadata as they don't compare well
        # as nested dictionaries with differing ids. Individual goal elements
        # are the same however.
        self.assertEqual(
            unpacked_step.goal.__dict__,
            step_metadata.goal.__dict__)
        del step_metadata.goal
        del unpacked_step.goal
        self.assertEqual(unpacked_step.__dict__, step_metadata.__dict__)

    def test_ext_unpack_with_tuple(self):
        test_tuple = (1, 'a')
        test_data = b'\x92\x01\xa1a'
        unpacked_tuple = self.serializer._ext_unpack(code=2, data=test_data)
        self.assertIsInstance(unpacked_tuple, tuple)
        self.assertEqual(unpacked_tuple, test_tuple)

    def test_ext_unpack_with_image(self):
        # from (50,100) image of all black pixels (0,0,0)
        test_data = b'\xc4_\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x002' \
            b'\x00\x00\x00d\x08\x02\x00\x00\x00K\x8a\xf4\x0c\x00\x00\x00' \
            b'&IDATx\x9c\xed\xc11\x01\x00\x00\x00\xc2\xa0\xf5Om\r\x0f' \
            b'\xa0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' \
            b'\x00\x00\xe0\xc3\x00:\xfc\x00\x01\xc0gM\x95\x00\x00\x00' \
            b'\x00IEND\xaeB`\x82'
        unpacked_image = self.serializer._ext_unpack(3, test_data)
        self.assertIsInstance(unpacked_image, PIL.Image.Image)
        self.assertEqual(unpacked_image.size, (50, 100))
        self.assertTrue(all(pixel == (0, 0, 0)
                            for pixel in unpacked_image.getdata()))

    def test_ext_unpack_with_goalmetadata(self):
        # from default GoalMetadata()
        test_data = b'\x97\xc0\xa0\xa0\x00\x00\xc0\x80'
        unpacked_goal = self.serializer._ext_unpack(4, test_data)
        self.assertIsInstance(unpacked_goal, GoalMetadata)
        self.assertEqual(unpacked_goal.__dict__, GoalMetadata().__dict__)

    def test_ext_unpack_with_objectmetadata(self):
        # from default ObjectMetadata()
        obj_data = b'\xdc\x00\x10\xa0\x90\x80\xcb\xbf\xf0\x00\x00\x00\x00' \
            b'\x00\x00\xcb\xbf\xf0\x00\x00\x00\x00\x00\x00\xcb\xbf\xf0\x00' \
            b'\x00\x00\x00\x00\x00\xc2\xcb\x00\x00\x00\x00\x00\x00\x00\x00' \
            b'\x90\x80\x80\x80\xa0\x90\x90\xc2'
        unpacked_objectmetadata = self.serializer._ext_unpack(
            code=5, data=obj_data)
        self.assertIsInstance(unpacked_objectmetadata, ObjectMetadata)
        self.assertEqual(
            unpacked_objectmetadata.__dict__,
            ObjectMetadata().__dict__)

    def test_ext_unpack_with_ndarray(self):
        # from [0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
        test_data = b'\x9a\xcb\x00\x00\x00\x00\x00\x00\x00\x00\xcb\x00\x00' \
            b'\x00\x00\x00\x00\x00\x00\xcb\x00\x00\x00\x00\x00\x00\x00\x00' \
            b'\xcb\x00\x00\x00\x00\x00\x00\x00\x00\xcb\x00\x00\x00\x00\x00' \
            b'\x00\x00\x00\xcb\x00\x00\x00\x00\x00\x00\x00\x00\xcb\x00\x00' \
            b'\x00\x00\x00\x00\x00\x00\xcb\x00\x00\x00\x00\x00\x00\x00\x00' \
            b'\xcb\x00\x00\x00\x00\x00\x00\x00\x00\xcb\x00\x00\x00\x00\x00' \
            b'\x00\x00\x00'
        unpacked_ndarray = self.serializer._ext_unpack(6, test_data)
        self.assertIsInstance(unpacked_ndarray, np.ndarray)
        self.assertFalse(np.all(unpacked_ndarray))
        self.assertEqual(unpacked_ndarray.size, 10)


class TestSerializerJson(unittest.TestCase):

    maxDiff = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.serializer = mcs.SerializerJson()
        return super().setUpClass()

    def test_serialize(self):
        step_metadata = StepMetadata()
        packed_json = self.serializer.serialize(step_metadata)
        self.assertIsInstance(packed_json, str)

    @skip
    def test_deserializer(self):
        step_metadata = StepMetadata()
        packed_json = self.serializer.serialize(step_metadata)
        self.assertIsInstance(packed_json, str)

        unpacked_step_metadata = self.serializer.deserialize(packed_json)
        self.assertIsInstance(unpacked_step_metadata, StepMetadata)

        # compare the two default StepMetadata objects
        self.assertEqual(
            unpacked_step_metadata.goal.__dict__,
            step_metadata.goal.__dict__)
        del step_metadata.goal
        del unpacked_step_metadata.goal
        self.assertEqual(
            unpacked_step_metadata.__dict__,
            step_metadata.__dict__)

    def test_ext_unpack(self):
        ...

    def test_mcs_step_metadata_encoder(self):
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(
            self.TestMcsStepMetadataEncoder)
        unittest.TextTestRunner(verbosity=2).run(suite)

    class TestMcsStepMetadataEncoder(unittest.TestCase):

        @classmethod
        def setUpClass(cls) -> None:
            cls.encoder = SerializerJson.McsStepMetadataEncoder()

        def test_default_with_tuple(self):
            test_tuple = (1, 'a')
            print(test_tuple)
            tuple_exttype = self.encoder.default(test_tuple)
            print(tuple_exttype)
            print(type(tuple_exttype))


@skip
class TestSerializer(unittest.TestCase):

    # TODO remove the permanent mgpack file resource

    @ staticmethod
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
