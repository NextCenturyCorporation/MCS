# import pytest

from machine_common_sense.serializer import *


def _helper_get_step_metadata():
    with open('./test.msgpack', 'rb') as file:
        packed_bytes = file.read()

    serializer = SerializerMsgPack()
    return serializer.deserialize(packed_bytes)


def test_serialization_msgpack():
    unpacked_metadata = _helper_get_step_metadata()
    assert unpacked_metadata.reward == 0.0, 'Reward unexpected.'
    assert unpacked_metadata.rotation == 0.0, 'Rotation unexpected.'


def test_serialization_json():
    unpacked_metadata = _helper_get_step_metadata()

    serializer = SerializerJson()
    json_dump = serializer.serialize(unpacked_metadata)
    unpacked_metadata = serializer.deserialize(json_dump)
    assert len(unpacked_metadata.depth_map_list) == 1, 'Depth map list length unexpected.'
    assert type(unpacked_metadata.depth_map_list[0]) == np.ndarray, 'Depth map type unexpected.'
    assert unpacked_metadata.depth_map_list[0].shape == (400, 600), ''
    assert type(unpacked_metadata) == StepMetadata, 'JSON deserialized object is not of type StepMetadata'
    assert unpacked_metadata.reward == 0.0, 'Reward unexpected.'
    assert unpacked_metadata.rotation == 0.0, 'Rotation unexpected.'
