import copy
from abc import ABC, abstractmethod
import logging
import math
import random
from typing import Tuple, Dict, Any, Type

import containers
import exceptions
import geometry
import objects
import util
from geometry import ROOM_DIMENSIONS, MIN_START_DISTANCE_AWAY

MAX_PLACEMENT_TRIES = 100
PERFORMER_BOUNDS = ((ROOM_DIMENSIONS[0][0] + MIN_START_DISTANCE_AWAY,
                     ROOM_DIMENSIONS[0][1] - MIN_START_DISTANCE_AWAY),
                    (ROOM_DIMENSIONS[1][0] + MIN_START_DISTANCE_AWAY,
                     ROOM_DIMENSIONS[1][1] - MIN_START_DISTANCE_AWAY))
"""(minX, maxX), (minZ, maxZ) for the performer (leaving space to put
an object in front of it)"""
                    

def move_to_location(obj_def: Dict[str, Any], obj: Dict[str, Any],
                     location: Dict[str, Any]):
    """Move the passed object to a new location"""
    obj['original_location'] = copy.deepcopy(location)
    new_location = copy.deepcopy(location)
    if 'offset' in obj_def:
        new_location['position']['x'] -= obj_def['offset']['x']
        new_location['position']['z'] -= obj_def['offset']['z']
    obj['shows'][0]['position'] = new_location['position']
    obj['shows'][0]['rotation'] = new_location['rotation']
    if 'bounding_box' in new_location:
        obj['shows'][0]['bounding_box'] = new_location['bounding_box']


class InteractionPair(ABC):
    def __init__(self, template: Dict[str, Any], find_path: bool):
        self._template = template
        self._find_path = find_path
        self._compute_performer_start()

    @abstractmethod
    def get_scenes(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        pass

    def _compute_performer_start(self) -> None:
        """Set the starting location (position & rotation) for the performer
        (_performer_start). This default implementation chooses a
        random location.
        """
        if getattr(self, '_performer_start', None) is None:
            self._performer_start = {
                'position': {
                    'x': round(random.uniform(PERFORMER_BOUNDS[0][0], PERFORMER_BOUNDS[0][1]), geometry.POSITION_DIGITS),
                    'y': 0,
                    'z': round(random.uniform(PERFORMER_BOUNDS[1][0], PERFORMER_BOUNDS[1][1]), geometry.POSITION_DIGITS)
                },
                'rotation': {
                    'y': geometry.random_rotation()
                }
            }

    def _get_empty_scene(self) -> Dict[str, Any]:
        scene = copy.deepcopy(self._template)
        scene['performerStart'] = self._performer_start
        return scene


class ImmediatelyVisiblePair(InteractionPair):
    def __init__(self, template: Dict[str, Any], find_path: bool):
        super(ImmediatelyVisiblePair, self).__init__(template, find_path)
        logging.debug(f'performerStart={self._performer_start}')

    def get_scenes(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        # choose target object
        target_def = util.finalize_object_definition(random.choice(objects.get_all_object_defs()))
        scene1 = self._get_empty_scene()
        # place target object in scene 1 right in front of the performer
        for _ in range(MAX_PLACEMENT_TRIES):
            in_front_location = geometry.get_location_in_front_of_performer(self._performer_start, target_def)
            if in_front_location is not None:
                break
        if in_front_location is None:
            raise exceptions.SceneException('could not place object in front of performer')
        logging.debug(f'position in front={in_front_location["position"]}')
        target = util.instantiate_object(target_def, in_front_location)
        scene1['objects'] = [target]
        scene2 = self._get_empty_scene()
        # place target object in scene 2 behind the performer
        for _ in range(MAX_PLACEMENT_TRIES):
            behind_location = geometry.get_location_behind_performer(self._performer_start, target_def)
            if behind_location is not None:
                break
        if behind_location is None:
            raise exceptions.SceneException('could not place object behind performer')
        logging.debug(f'position behind={behind_location["position"]}')
        target2 = copy.deepcopy(target)
        move_to_location(target_def, target2, behind_location)
        scene2['objects'] = [target2]
        return scene1, scene2


class HiddenBehindPair(InteractionPair):
    def __init__(self, template: Dict[str, Any], find_path: bool):
        super(HiddenBehindPair, self).__init__(template, find_path)

    def get_scenes(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        for _ in range(MAX_PLACEMENT_TRIES):
            target_def = util.finalize_object_definition(random.choice(objects.get_all_object_defs()))
            occluder_defs = geometry.get_wider_and_taller_defs(target_def)
            if occluder_defs is not None:
                break
        if occluder_defs is None:
            raise exceptions.SceneException('could not get a target and occluder')
        occluder_def = util.finalize_object_definition(random.choice(occluder_defs))

        scene1 = self._get_empty_scene()
        # place target object in scene 1 right in front of the performer
        for _ in range(MAX_PLACEMENT_TRIES):
            in_front_location = geometry.get_location_in_front_of_performer(self._performer_start, target_def)
            if in_front_location is not None:
                break
        if in_front_location is None:
            raise exceptions.SceneException('could not place target in front of performer')
        target = util.instantiate_object(target_def, in_front_location)
        scene1['objects'] = [target]

        # place occluder right in front of performer in scene 2
        for _ in range(MAX_PLACEMENT_TRIES):
            in_front_location = geometry.get_location_in_front_of_performer(self._performer_start, occluder_def,
                                                                            lambda: 0)
            if in_front_location is not None:
                break
        if in_front_location is None:
            raise exceptions.SceneException('could not place occluder in front of performer')
        # Rotate occluder to be facing the performer. There is a
        # chance that this rotation could cause the occluder to
        # intersect the wall of the room, because it's different from
        # the rotation returned by get_location_in_front_of_performer
        # (which does check for that). But it seems pretty unlikely.
        dx = self._performer_start['position']['x'] - in_front_location['position']['x']
        dz = self._performer_start['position']['z'] - in_front_location['position']['z']
        angle = math.degrees(math.atan2(dz, dx))
        # negative because we do clockwise rotation
        in_front_location['rotation']['y'] = -angle
        occluder = util.instantiate_object(occluder_def, in_front_location)
        occluded_location = geometry.get_adjacent_location_on_side(target_def,
                                                                   occluder,
                                                                   self._performer_start['position'],
                                                                   2)
        if occluded_location is None:
            raise exceptions.SceneException('could not place target behind occluder')
        target2 = copy.deepcopy(target)
        move_to_location(target_def, target2, occluded_location)
        scene2 = self._get_empty_scene()
        scene2['objects'] = [target2, occluder]

        return scene1, scene2
    

class SimilarAdjacentPair(InteractionPair):
    def __init__(self, template: Dict[str, Any], find_path: bool):
        super(SimilarAdjacentPair, self).__init__(template, find_path)

    def get_scenes(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        target_def = util.finalize_object_definition(random.choice(objects.get_all_object_defs()))
        target_location = geometry.calc_obj_pos(self._performer_start['position'], [], target_def)
        target = util.instantiate_object(target_def, target_location)
        similar_def = util.finalize_object_definition(util.get_similar_definition(target))
        container = None
        if random.random() <= util.TARGET_CONTAINED_CHANCE:
            container_defs = objects.get_enclosed_containers().copy()
            random.shuffle(container_defs)
            for container_def in container_defs:
                placement = containers.can_contain_both(container_def, target_def, similar_def)
                if placement is not None:
                    break
            if placement is not None:
                container_def, index, orientation, rot_a, rot_b = placement
                container_def = util.finalize_object_definition(container_def)
                container_location = geometry. \
                    calc_obj_pos(self._performer_start['position'], [], container_def)
                container = util.instantiate_object(container_def, container_location)
                containers.put_object_in_container(target, container, container_def, index)
        scene1 = self._get_empty_scene()
        scene1['objects'] = [target] if container is None else [target, container]

        similar_location = geometry. \
            get_adjacent_location(similar_def, target,
                                  self._performer_start['position'])
        if similar_location is None:
            raise exceptions.SceneException('could not place similar object adjacent to target')
        similar = util.instantiate_object(similar_def, similar_location)
        scene2 = self._get_empty_scene()
        if container is None:
            scene2['objects'] = [target, similar]
        else:
            target2 = copy.deepcopy(target)
            containers.put_objects_in_container(target2, similar, container,
                                                container_def, index, orientation,
                                                rot_a, rot_b)
            scene2['objects'] = [target2, similar, container]

        return scene1, scene2


class SimilarAdjacentContainedPair(InteractionPair):
    def __init__(self, template: Dict[str, Any], find_path: bool):
        super(SimilarAdjacentContainedPair, self).__init__(template, find_path)

    def get_scenes(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        for _ in range(MAX_PLACEMENT_TRIES):
            target_def = util.finalize_object_definition(random.choice(objects.get_all_object_defs()))
            target_location = geometry.calc_obj_pos(self._performer_start['position'], [], target_def)
            target = util.instantiate_object(target_def, target_location)
            similar_def = util.get_similar_definition(target)
            similar = util.instantiate_object(similar_def, geometry.ORIGIN_LOCATION)
            # find a container big enough for both of them
            valid_container_defs = containers.get_enclosable_container_defs((target, similar))
            if len(valid_container_defs) > 0:
                break
        if len(valid_container_defs) == 0:
            raise exceptions.SceneException(f'failed to find target and/or similar object that will fit in something')
        container_def = util.finalize_object_definition(random.choice(valid_container_defs))
        container_location = geometry.get_adjacent_location(container_def,
                                                            target,
                                                            self._performer_start['position'])
        container = util.instantiate_object(container_def, container_location)
        area_index = containers.can_contain(container_def, target, similar)
        if area_index is None:
            raise exceptions.SceneException('internal error: container should be big enough but is not')
        containers.put_object_in_container(similar, container, container_def, area_index)

        scene1 = self._get_empty_scene()
        scene1['objects'] = [target, similar, container]

        target2 = copy.deepcopy(target)
        container2 = copy.deepcopy(container)
        containers.put_object_in_container(target2, container2, container_def, area_index)
        similar2 = copy.deepcopy(similar)
        del similar2['locationParent']
        similar2_location = geometry.get_adjacent_location(similar_def,
                                                           container2,
                                                           self._performer_start['position'])
        move_to_location(similar_def, similar2, similar2_location)
        scene2 = self._get_empty_scene()
        scene2['objects'] = [target2, similar2, container2]

        return scene1, scene2


#_INTERACTION_PAIR_CLASSES = [HiddenBehindPair, ImmediatelyVisiblePair, SimilarAdjacentContainedPair]
_INTERACTION_PAIR_CLASSES = [SimilarAdjacentPair]


def get_pair_class() -> Type[InteractionPair]:
    return random.choice(_INTERACTION_PAIR_CLASSES)
