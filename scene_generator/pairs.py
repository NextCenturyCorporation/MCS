import copy
from abc import ABC, abstractmethod
import logging
import random
from typing import Tuple, Dict, Any, Type, Optional

import shapely

import exceptions
import geometry
import objects
import util
from geometry import ROOM_DIMENSIONS, MIN_START_DISTANCE_AWAY

MAX_EXTRA_OBJECTS = 10
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
    obj['shows'][0]['bounding_box'] = new_location['bounding_box']


def add_objects(target: Dict[str, Any], performer_position: Dict[str, float], scene: Dict[str, Any]):
    """Add 0 to MAX_EXTRA_OBJECTS to the scene with none between the
    performer and the target.
    """
    all_obj_defs = objects.get_all_object_defs()
    target_x = target['shows'][0]['position']['x']
    target_z = target['shows'][0]['position']['z']
    target_coords = geometry.calc_obj_coords(target_x, target_z,
                                             target['dimensions']['x'] / 2.0,
                                             target['dimensions']['z'] / 2.0,
                                             0, 0, target['shows'][0]['rotation']['y'])
    # init with the rect for the target
    rects = [target_coords]
    num_extra_objects = random.randint(0, MAX_EXTRA_OBJECTS)
    for _ in range(num_extra_objects):
        found_location = False
        for dummy in range(util.MAX_TRIES):
            obj_def = util.finalize_object_definition(random.choice(all_obj_defs))
            location = geometry.calc_obj_pos(performer_position, rects, obj_def)
            rect = rects[-1]
            rect_as_poly = shapely.geometry.Polygon([(point['x'], point['z']) for point in rect])
            # check intersection of rect_coords with line between target and performer
            visible_segment = shapely.geometry.LineString([(performer_position['x'],
                                                           performer_position['z']),
                                                           (target_x, target_z)])
            if rect_as_poly.intersects(visible_segment):
                # reject it
                rects.pop()
            else:
                found_location = True
                break
        if found_location:
            new_obj = util.instantiate_object(obj_def, location)
            scene['objects'].append(new_obj)


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


class ImmediatelyVisiblePair(InteractionPair):
    def __init__(self, template: Dict[str, Any], find_path: bool):
        super(ImmediatelyVisiblePair, self).__init__(template, find_path)
        logging.debug(f'performerStart={self._performer_start}')

    def _get_empty_scene(self) -> Dict[str, Any]:
        scene = copy.deepcopy(self._template)
        scene['performerStart'] = self._performer_start
        return scene

    def _get_locations(self, target_def: Dict[str, Any]) -> \
            Optional[Tuple[Dict[str, Any], Dict[str, Any]]]:
        # place target object in scene 1 right in front of the performer
        for _ in range(util.MAX_TRIES):
            in_front_location = geometry.\
                get_location_in_front_of_performer(self._performer_start, target_def)
            if in_front_location is not None:
                break
        if in_front_location is None:
            return None
        
        # place target object in scene 2 behind the performer
        for _ in range(util.MAX_TRIES):
            behind_location = geometry.get_location_behind_performer(self._performer_start, target_def)
            if behind_location is not None:
                break
        if behind_location is None:
            return None

        return in_front_location, behind_location

    def get_scenes(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        # choose target object
        target_def = util.finalize_object_definition(random.choice(objects.get_all_object_defs()))
        for _ in range(util.MAX_TRIES):
            locations = self._get_locations(target_def)
            if locations is not None:
                break
            self._performer_start = None
            self._compute_performer_start()
        if locations is None:
            raise exceptions.SceneException('could not place performer with objects in front and behind')
        in_front_location, behind_location = locations

        scene1 = self._get_empty_scene()
        target = util.instantiate_object(target_def, in_front_location)
        scene1['objects'] = [target]
        add_objects(target, self._performer_start['position'], scene1)
        
        scene2 = self._get_empty_scene()
        target2 = copy.deepcopy(target)
        move_to_location(target_def, target2, behind_location)
        scene2['objects'] = [target2]
        add_objects(target, self._performer_start['position'], scene2)
        return scene1, scene2


_INTERACTION_PAIR_CLASSES = [ImmediatelyVisiblePair]


def get_pair_class() -> Type[InteractionPair]:
    return random.choice(_INTERACTION_PAIR_CLASSES)
