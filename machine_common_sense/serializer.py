import io
import json
from abc import ABCMeta, abstractmethod
from typing import Dict, Union

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
                    x.image_list, x.object_list, x.object_mask_list, x.pose,
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
                    x.uuid, x.color, x.dimensions, x.direction, x.distance,
                    x.distance_in_steps, x.distance_in_world, x.held, x.mass,
                    x.material_list, x.position, x.rotation, x.shape,
                    x.state_list, x.texture_color_list, x.visible
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
                head_tilt, image_list, object_list, object_mask_list, pose, \
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
                                pose=pose,
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
        serialized = msgpack.packb(step_metadata,
                                   default=SerializerMsgPack._ext_pack,
                                   strict_types=True)
        return serialized

    @staticmethod
    def deserialize(packed_step_metadata):
        deserialized = msgpack.unpackb(packed_step_metadata,
                                       ext_hook=SerializerMsgPack._ext_unpack)
        return deserialized


class SerializerJson(ISerializer):
    """Serializer to (de)serialize StepMetadata into/from MsgPack format."""
    class McsStepMetadataEncoder(json.JSONEncoder):
        """
        JSON Encoder Class for MCS Step Metadata, e.g.
        json_dump = json.dumps(output, cls=McsStepMetadataEncoder, indent=4)
        """

        # Empty docstring here to override superclass function docstring.
        def default(self, x):
            """"""
            if isinstance(x, StepMetadata):
                return {
                    'action_list': x.action_list,
                    'camera_aspect_ratio': x.camera_aspect_ratio,
                    'camera_clipping_planes': x.camera_clipping_planes,
                    'camera_field_of_view': x.camera_field_of_view,
                    'camera_height': x.camera_height,
                    'depth_map_list': x.depth_map_list,
                    'goal': x.goal,
                    'head_tilt': x.head_tilt,
                    'image_list': x.image_list,
                    'object_list': x.object_list,
                    'object_mask_list': x.object_mask_list,
                    'pose': x.pose,
                    'position': x.position,
                    'return_status': x.return_status,
                    'reward': x.reward,
                    'rotation': x.rotation,
                    'step_number': x.step_number,
                    'structural_object_list': x.structural_object_list
                }
            elif isinstance(x, tuple):
                return [x[0], x[1]]
            elif isinstance(x, Image.Image):
                # Could also use: return x.tobytes().decode("latin1")
                # or: buffer = BytesIO() x.save(buff, format="PNG")
                #     base64.b64encode(buffer.getvalue()).decode('ascii')
                return np.array(x).tolist()
            elif isinstance(x, GoalMetadata):
                return {
                    'action_list': x.action_list,
                    'category': x.category,
                    'description': x.description,
                    'habituation_total': x.habituation_total,
                    'last_preview_phase_step': x.last_preview_phase_step,
                    'last_step': x.last_step,
                    'metadata': x.metadata
                }
            elif isinstance(x, ObjectMetadata):
                return {
                    'uuid': x.uuid,
                    'dimensions': x.dimensions,
                    'direction': x.direction,
                    'distance': x.distance,
                    'distance_in_steps': x.distance_in_steps,
                    'distance_in_world': x.distance_in_world,
                    'held': x.held,
                    'mass': x.mass,
                    'material_list': x.material_list,
                    'position': x.position,
                    'rotation': x.rotation,
                    'segment_color': x.segment_color,
                    'shape': x.shape,
                    'state_list': x.state_list,
                    'texture_color_list': x.texture_color_list,
                    'visible': x.visible
                }
            elif isinstance(x, np.ndarray):
                return x.tolist()
            return json.JSONEncoder.default(self, x)

    @staticmethod
    def convert_object_list(raw_list):
        """Iterates over JSON object list and creates ObjectMetadata objects
        for each JSON object.
        """
        object_list = []
        for object_raw in raw_list:
            obj = ObjectMetadata(
                object_raw['uuid'],
                object_raw['dimensions'],
                object_raw['direction'],
                object_raw['distance'],
                object_raw['distance_in_steps'],
                object_raw['distance_in_world'],
                object_raw['held'],
                object_raw['mass'],
                object_raw['material_list'],
                object_raw['position'],
                object_raw['rotation'],
                object_raw['segment_color'],
                object_raw['shape'],
                object_raw['state_list'],
                object_raw['texture_color_list'],
                object_raw['visible'])
            object_list.append(obj)
        return object_list

    @staticmethod
    def serialize(step_metadata: StepMetadata, indent: int = 4):
        json_dump = json.dumps(step_metadata,
                               cls=SerializerJson.McsStepMetadataEncoder,
                               indent=indent)
        return json_dump

    @staticmethod
    def deserialize(input_json: Union[Dict, str]):
        if isinstance(input_json, str):
            input_json = json.loads(input_json)
        depth_map_list = []
        for depth_map_raw in input_json['depth_map_list']:
            depth_map_list.append(np.array(depth_map_raw, dtype='uint8'))

        object_mask_list = []
        for obj_mask_raw in input_json['object_mask_list']:
            object_mask_list.append(np.array(obj_mask_raw, dtype='uint8'))

        image_list = []
        for img_raw in input_json['image_list']:  # PIL
            image_list.append(Image.fromarray(np.array(img_raw,
                                                       dtype='uint8')))

        object_list_raw = input_json['object_list']
        object_list = SerializerJson.convert_object_list(object_list_raw)

        structural_object_list_raw = input_json['structural_object_list']
        structural_object_list = SerializerJson.convert_object_list(
            structural_object_list_raw)

        goal_raw = input_json['goal']
        goal = GoalMetadata(goal_raw['action_list'], goal_raw['category'],
                            goal_raw['description'],
                            goal_raw['habituation_total'],
                            goal_raw['last_preview_phase_step'],
                            goal_raw['last_step'], goal_raw['metadata'])

        return StepMetadata(
            action_list=input_json['action_list'],
            camera_aspect_ratio=input_json['camera_aspect_ratio'],
            camera_clipping_planes=input_json['camera_clipping_planes'],
            camera_field_of_view=input_json['camera_field_of_view'],
            camera_height=input_json['camera_height'],
            depth_map_list=depth_map_list,
            goal=goal,
            head_tilt=input_json['head_tilt'],
            image_list=image_list,
            object_list=object_list,
            object_mask_list=object_mask_list,
            pose=input_json['pose'],
            position=input_json['position'],
            return_status=input_json['return_status'],
            reward=input_json['reward'],
            rotation=input_json['rotation'],
            step_number=input_json['step_number'],
            structural_object_list=structural_object_list)
