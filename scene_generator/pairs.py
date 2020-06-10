import copy
from abc import ABC, abstractmethod
import logging
import random
from typing import Tuple, Dict, Any, Type

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
            valid_container_defs = geometry.get_enclosable_container_defs((target, similar))
            if len(valid_container_defs) > 0:
                break
        if len(valid_container_defs) == 0:
            raise exceptions.SceneException(f'failed to find target and/or similar object that will fit in something')
        container_def = util.finalize_object_definition(random.choice(valid_container_defs))
        container_location = geometry.get_adjacent_location(container_def,
                                                            target,
                                                            self._performer_start['position'])
        container = util.instantiate_object(container_def, container_location)
        area_index = geometry.can_contain(container_def, target, similar)
        if area_index is None:
            raise exceptions.SceneException('internal error: container should be big enough but is not')
        util.put_object_in_container(similar, container, container_def, area_index)

        scene1 = self._get_empty_scene()
        scene1['objects'] = [target, similar, container]

        target2 = copy.deepcopy(target)
        container2 = copy.deepcopy(container)
        util.put_object_in_container(target2, container2, container_def, area_index)
        similar2 = copy.deepcopy(similar)
        del similar2['locationParent']
        similar2_location = geometry.get_adjacent_location(similar_def,
                                                           container2,
                                                           self._performer_start['position'])
        move_to_location(similar_def, similar2, similar2_location)
        scene2 = self._get_empty_scene()
        scene2['objects'] = [target2, similar2, container2]

        return scene1, scene2


_INTERACTION_PAIR_CLASSES = [ImmediatelyVisiblePair, SimilarAdjacentContainedPair]


def get_pair_class() -> Type[InteractionPair]:
    return random.choice(_INTERACTION_PAIR_CLASSES)
