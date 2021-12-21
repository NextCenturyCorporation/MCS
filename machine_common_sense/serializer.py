import io
from abc import ABCMeta, abstractmethod

import msgpack
import numpy as np
import PIL.Image as Image

from .goal_metadata import GoalMetadata
from .object_metadata import ObjectMetadata
from .step_metadata import StepMetadata


class ISerializer:
    __metaclass__ = ABCMeta

    @classmethod
    def version(cls):
        return "0.1.0"

    @staticmethod
    @abstractmethod
    def serialize(unpacked_object):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def deserialize(packed_object):
        raise NotImplementedError

    @staticmethod
    def image_to_bytes(image):
        """Converts PIL image to bytes."""
        byte_io = io.BytesIO()
        image.save(byte_io, format='PNG')
        return byte_io.getvalue()

    @staticmethod
    def bytes_to_image(bytes_image):
        """Converts bytes to PIL image."""
        return Image.open(io.BytesIO(bytes_image))


class SerializerMsgPack(ISerializer):
    """Serializer to (de)serialize StepMetadata into/from MsgPack format."""

    @staticmethod
    def _ext_pack(x):
        """Hook to serialize MCS Step Metadata as MsgPack, e.g.
        serialized = msgpack.packb(output, default=ext_pack, strict_types=True)
        """
        if isinstance(x, StepMetadata):
            # TODO In future can investigate reflection for automating field
            # extraction, but notice that strict types flag is highly
            # dependent on order. Something like this might be a start:
            # [field for field in dir(x) if not callable(getattr(x, field))
            # and not field.startswith("__")]
            return msgpack.ExtType(
                1,
                msgpack.packb([
                    x.action_list, x.camera_aspect_ratio,
                    x.camera_clipping_planes, x.camera_field_of_view,
                    x.camera_height, x.depth_map_list, x.goal, x.head_tilt,
                    x.image_list, x.object_list, x.object_mask_list,
                    x.position, x.return_status, x.reward, x.rotation,
                    x.step_number, x.structural_object_list
                ],
                    default=SerializerMsgPack._ext_pack,
                    strict_types=True))
        elif isinstance(x, tuple):
            return msgpack.ExtType(
                2,
                msgpack.packb([x[0], x[1]],
                              default=SerializerMsgPack._ext_pack,
                              strict_types=True))
        elif isinstance(x, Image.Image):
            return msgpack.ExtType(
                3,
                msgpack.packb(SerializerMsgPack.image_to_bytes(x),
                              default=SerializerMsgPack._ext_pack,
                              strict_types=True))
        elif isinstance(x, GoalMetadata):
            return msgpack.ExtType(
                4,
                msgpack.packb([
                    x.action_list, x.category, x.description,
                    x.habituation_total, x.last_preview_phase_step,
                    x.last_step, x.metadata
                ],
                    default=SerializerMsgPack._ext_pack,
                    strict_types=True))
        elif isinstance(x, ObjectMetadata):
            return msgpack.ExtType(
                5,
                msgpack.packb([
                    x.uuid, x.dimensions, x.direction, x.distance,
                    x.distance_in_steps, x.distance_in_world, x.held, x.mass,
                    x.material_list, x.position, x.rotation, x.segment_color,
                    x.shape, x.state_list, x.texture_color_list, x.visible
                ],
                    default=SerializerMsgPack._ext_pack,
                    strict_types=True))
        elif isinstance(x, np.ndarray):
            return msgpack.ExtType(
                6,
                msgpack.packb(x.tolist(),
                              default=SerializerMsgPack._ext_pack,
                              strict_types=True))
        return x

    @staticmethod
    def _ext_unpack(code, data):
        """
        Hook to deserialize MCS Step Metadata from MsgPack, e.g.
        deserialized = msgpack.unpackb(packed_bytes, ext_hook=ext_unpack)
        """
        if code == 1:
            action_list, camera_aspect_ratio, camera_clipping_planes, \
                camera_field_of_view, camera_height, depth_map_list, goal, \
                head_tilt, image_list, object_list, object_mask_list, \
                position, return_status, reward, rotation, step_number, \
                structural_object_list = \
                msgpack.unpackb(data, ext_hook=SerializerMsgPack._ext_unpack)
            return StepMetadata(action_list=action_list,
                                camera_aspect_ratio=camera_aspect_ratio,
                                camera_clipping_planes=camera_clipping_planes,
                                camera_field_of_view=camera_field_of_view,
                                camera_height=camera_height,
                                depth_map_list=depth_map_list,
                                goal=goal,
                                head_tilt=head_tilt,
                                image_list=image_list,
                                object_list=object_list,
                                object_mask_list=object_mask_list,
                                position=position,
                                return_status=return_status,
                                reward=reward,
                                rotation=rotation,
                                step_number=step_number,
                                structural_object_list=structural_object_list)
        elif code == 2:
            x0, x1 = msgpack.unpackb(data,
                                     ext_hook=SerializerMsgPack._ext_unpack)
            return x0, x1
        elif code == 3:
            x = msgpack.unpackb(data, ext_hook=SerializerMsgPack._ext_unpack)
            return SerializerMsgPack.bytes_to_image(x)
        elif code == 4:
            action_list, category, description, habituation_total, \
                last_preview_phase_step, last_step, metadata = \
                msgpack.unpackb(data, ext_hook=SerializerMsgPack._ext_unpack)
            return GoalMetadata(action_list, category, description,
                                habituation_total, last_preview_phase_step,
                                last_step, metadata)
        elif code == 5:
            uuid, dimensions, direction, distance, distance_in_steps, \
                distance_in_world, held, mass, material_list, position, \
                rotation, segment_color, shape, state_list, \
                texture_color_list, visible = msgpack.unpackb(
                    data, ext_hook=SerializerMsgPack._ext_unpack)
            return ObjectMetadata(uuid, dimensions, direction, distance,
                                  distance_in_steps, distance_in_world, held,
                                  mass, material_list, position, rotation,
                                  segment_color, shape, state_list,
                                  texture_color_list, visible)
        elif code == 6:
            x = msgpack.unpackb(data, ext_hook=SerializerMsgPack._ext_unpack)
            return np.asarray(x)
        return msgpack.ExtType(code, data)

    @staticmethod
    def serialize(step_metadata: StepMetadata):
        """
        Serializes step metadata into MsgPack.

        You can use
        .. code-block:: python

            object_to_persist = {
                'payload': step_metadata,
                'additional_info': 'info'
                }

        to add extra data.

        Args:
            step_metadata: MCS step metadata output

        Returns:
            Serialized version of step metadata in MsgPack format.
        """
        return msgpack.packb(step_metadata,
                             default=SerializerMsgPack._ext_pack,
                             strict_types=True)

    @staticmethod
    def deserialize(packed_step_metadata):
        return msgpack.unpackb(packed_step_metadata,
                               ext_hook=SerializerMsgPack._ext_unpack)
