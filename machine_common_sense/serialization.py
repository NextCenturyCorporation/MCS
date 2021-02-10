from typing import Dict

import machine_common_sense as mcs
from machine_common_sense import GoalMetadata, ObjectMetadata, StepMetadata
import PIL.Image as Image
import io
import json
import msgpack
import numpy as np
import pathlib


def image_to_bytes(image):
    """Converts PIL image to bytes."""
    byte_io = io.BytesIO()
    image.save(byte_io, format='PNG')
    return byte_io.getvalue()


def bytes_to_image(bytes_image):
    """Converts bytes to PIL image."""
    return Image.open(io.BytesIO(bytes_image))


def ext_pack(x):
    """
    Serializes MCS Step Metadata as MsgPack, e.g.
    serialized = msgpack.packb(output, default=ext_pack, strict_types=True)
    """
    if isinstance(x, StepMetadata):
        return msgpack.ExtType(1, msgpack.packb([x.action_list, x.camera_aspect_ratio, x.camera_clipping_planes,
                                                 x.camera_field_of_view, x.camera_height, x.depth_map_list, x.goal,
                                                 x.head_tilt, x.image_list, x.object_list, x.object_mask_list, x.pose,
                                                 x.position, x.return_status, x.reward, x.rotation, x.step_number,
                                                 x.structural_object_list], default=ext_pack, strict_types=True))
    elif isinstance(x, tuple):
        return msgpack.ExtType(2, msgpack.packb([x[0], x[1]], default=ext_pack, strict_types=True))
    elif isinstance(x, Image.Image):
        return msgpack.ExtType(3, msgpack.packb(image_to_bytes(x), default=ext_pack, strict_types=True))
    elif isinstance(x, GoalMetadata):
        return msgpack.ExtType(4, msgpack.packb([x.action_list, x.category, x.description, x.habituation_total,
                                                 x.last_preview_phase_step, x.last_step, x.metadata], default=ext_pack,
                                                strict_types=True))
    elif isinstance(x, ObjectMetadata):
        return msgpack.ExtType(5, msgpack.packb([x.uuid, x.color, x.dimensions, x.direction, x.distance,
                                                 x.distance_in_steps, x.distance_in_world, x.held, x.mass,
                                                 x.material_list, x.position, x.rotation, x.visible],
                                                default=ext_pack, strict_types=True))
    elif isinstance(x, np.ndarray):
        return msgpack.ExtType(6, msgpack.packb(x.tolist(), default=ext_pack, strict_types=True))
    return x


def ext_unpack(code, data):
    """
    Deserializes MCS Step Metadata from MsgPack, e.g.
    deserialized = msgpack.unpackb(packed_bytes, ext_hook=ext_unpack)
    """
    if code == 1:
        action_list, camera_aspect_ratio, camera_clipping_planes, camera_field_of_view, camera_height, depth_map_list, \
        goal, head_tilt, image_list, object_list, object_mask_list, pose, position, return_status, reward, rotation, \
        step_number, structural_object_list = msgpack.unpackb(data, ext_hook=ext_unpack)
        return StepMetadata(
                        action_list=action_list,
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
                        structural_object_list=structural_object_list
               )
    elif code == 2:
        x0, x1 = msgpack.unpackb(data, ext_hook=ext_unpack)
        return x0, x1
    elif code == 3:
        x = msgpack.unpackb(data, ext_hook=ext_unpack)
        return bytes_to_image(x)
    elif code == 4:
        action_list, category, description, habituation_total, last_preview_phase_step, last_step, metadata = \
            msgpack.unpackb(data, ext_hook=ext_unpack)
        return GoalMetadata(action_list, category, description, habituation_total, last_preview_phase_step, last_step,
                            metadata)
    elif code == 5:
        uuid, color, dimensions, direction, distance, distance_in_steps, distance_in_world, held, mass, material_list, \
        position, rotation, visible = msgpack.unpackb(data, ext_hook=ext_unpack)
        return ObjectMetadata(uuid, color, dimensions, direction, distance, distance_in_steps, distance_in_world,
                              held, mass, material_list, position, rotation, visible)
    elif code == 6:
        x = msgpack.unpackb(data, ext_hook=ext_unpack)
        return np.asarray(x)
    return msgpack.ExtType(code, data)


class McsStepMetadataEncoder(json.JSONEncoder):
    """
    JSON Encoder Class for MCS Step Metadata, e.g.
    json_dump = json.dumps(output, cls=McsStepMetadataEncoder, indent=4)
    """
    def default(self, x):
        if isinstance(x, StepMetadata):
            return {'action_list': x.action_list,
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
                    'structural_object_list': x.structural_object_list}
        elif isinstance(x, tuple):
            return [x[0], x[1]]
        elif isinstance(x, Image.Image):
            # Could also use: return x.tobytes().decode("latin1")
            # or: buff = BytesIO() image.save(buff, format="PNG")
            #     base64.b64encode(buff.getvalue()).decode('ascii')
            return np.array(x).tolist()
        elif isinstance(x, GoalMetadata):
            return {'action_list': x.action_list,
                    'category': x.category,
                    'description': x.description,
                    'habituation_total': x.habituation_total,
                    'last_preview_phase_step': x.last_preview_phase_step,
                    'last_step': x.last_step,
                    'metadata': x.metadata}
        elif isinstance(x, ObjectMetadata):
            return {'uuid': x.uuid,
                    'color': x.color,
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
                    'visible': x.visible}
        elif isinstance(x, np.ndarray):
            return x.tolist()
        return json.JSONEncoder.default(self, x)


def convert_object_list(raw_list):
    """Iterates over JSON object list and creates ObjectMetadata objects for each JSON object."""
    object_list = []
    for object_raw in raw_list:
        obj = ObjectMetadata(object_raw['uuid'],
                    object_raw['color'],
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
                    object_raw['visible'])
        object_list.append(obj)
    return object_list


def deserialize_step_metadata_from_json(input_json: Dict):
    depth_map_list = []
    for depth_map_raw in input_json['depth_map_list']:
        depth_map_list.append(np.array(depth_map_raw, dtype='uint8'))

    object_mask_list = []
    for obj_mask_raw in input_json['object_mask_list']:
        object_mask_list.append(np.array(obj_mask_raw, dtype='uint8'))

    image_list = []
    for img_raw in input_json['image_list']:  # PIL
        image_list.append(Image.fromarray(np.array(img_raw, dtype='uint8')))

    object_list_raw = input_json['object_list']
    object_list = convert_object_list(object_list_raw)

    structural_object_list_raw = input_json['structural_object_list']
    structural_object_list = convert_object_list(structural_object_list_raw)

    goal_raw = input_json['goal']
    goal = GoalMetadata(
        goal_raw['action_list'],
        goal_raw['category'],
        goal_raw['description'],
        goal_raw['habituation_total'],
        goal_raw['last_preview_phase_step'],
        goal_raw['last_step'],
        goal_raw['metadata'])

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
        structural_object_list=structural_object_list
    )
