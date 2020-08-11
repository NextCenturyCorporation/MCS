import logging
import random
import shapely
import uuid
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, Tuple, List, Optional

import geometry
import objects
import separating_axis_theorem
import tags
import util

MAX_WALL_WIDTH = 4
MIN_WALL_WIDTH = 1
WALL_Y_POS = 1.5
WALL_HEIGHT = 3
WALL_DEPTH = 0.1

DIST_WALL_APART = 1
SAFE_DIST_FROM_ROOM_WALL = 3.5


def generate_wall(wall_material: str,
                  wall_colors: List[str],
                  performer_position: Dict[str,
                                           float],
                  other_rects: List[List[Dict[str,
                                              float]]],
                  dont_obstruct_list: List[Dict[str,
                                                Any]] = None) -> Optional[Dict[str,
                                                                               Any]]:
    """Generates and returns a randomly positioned obstacle wall. If dont_obstruct_list is not None, the wall won't
    obstruct the line between the performer_position and the objects in dont_obstruct_list."""

    tries = 0
    performer_rect = geometry.find_performer_rect(performer_position)
    performer_poly = geometry.rect_to_poly(performer_rect)
    while tries < util.MAX_TRIES:
        rotation = random.choice((0, 90, 180, 270))
        new_x = geometry.random_position_x()
        new_z = geometry.random_position_z()
        new_x_size = round(
            random.uniform(
                MIN_WALL_WIDTH,
                MAX_WALL_WIDTH),
            geometry.POSITION_DIGITS)

        # Make sure the wall is not too close to the rooms 4 walls
        if ((rotation == 0 or rotation == 180) and (new_z < -SAFE_DIST_FROM_ROOM_WALL or new_z > SAFE_DIST_FROM_ROOM_WALL)) or \
                ((rotation == 90 or rotation == 270) and (new_x < -SAFE_DIST_FROM_ROOM_WALL or new_x > SAFE_DIST_FROM_ROOM_WALL)):
            continue

        rect = geometry.calc_obj_coords(
            new_x, new_z, new_x_size, WALL_DEPTH, 0, 0, rotation)
        # barrier_rect is to allow parallel walls to be at least
        # 1(DIST_WALL_APART) apart on the appropriate axis
        barrier_rect = geometry.calc_obj_coords(
            new_x,
            new_z,
            new_x_size +
            DIST_WALL_APART,
            WALL_DEPTH +
            DIST_WALL_APART,
            0,
            0,
            rotation)
        wall_poly = geometry.rect_to_poly(rect)
        is_ok = not wall_poly.intersects(performer_poly) and geometry.rect_within_room(rect) and (
            len(other_rects) == 0 or not any(
                separating_axis_theorem.sat_entry(
                    barrier_rect, other_rect) for other_rect in other_rects))
        if is_ok:
            if dont_obstruct_list:
                for dont_obstruct_object in dont_obstruct_list:
                    if 'locationParent' not in dont_obstruct_object and geometry.does_fully_obstruct_target(
                            performer_position, dont_obstruct_object, wall_poly):
                        is_ok = False
                        break
            if is_ok:
                break
        tries += 1

    if tries < util.MAX_TRIES:
        new_object = {
            'id': 'wall_' + str(uuid.uuid4()),
            'materials': [wall_material],
            'type': 'cube',
            'kinematic': 'true',
            'structure': 'true',
            'mass': 200,
            'info': wall_colors
        }
        shows_object = {
            'stepBegin': 0,
            'scale': {'x': new_x_size, 'y': WALL_HEIGHT, 'z': WALL_DEPTH},
            'rotation': {'x': 0, 'y': rotation, 'z': 0},
            'position': {'x': new_x, 'y': WALL_Y_POS, 'z': new_z},
            'boundingBox': rect
        }
        shows = [shows_object]
        new_object['shows'] = shows

        return new_object
    return None


class GoalCategory(Enum):
    """String for the goal's JSON config "category" property. Should all be listed in the API documentation."""
    INTPHYS = 'intphys'
    RETRIEVAL = 'retrieval'
    TRANSFERRAL = 'transferral'
    TRAVERSAL = 'traversal'


class Goal(ABC):
    """An abstract Goal. Subclasses must implement compute_objects and _get_subclass_config. Users of a goal object
    should normally only need to call update_body."""

    def __init__(self, name: str):
        self._name = name
        self._performer_start = None
        self._compute_performer_start()
        self._tag_to_objects = {}

    def update_body(self, body: Dict[str, Any],
                    find_path: bool) -> Dict[str, Any]:
        """Helper method that calls other Goal methods to set performerStart, objects, and goal. Returns the goal body
        object."""
        self._tag_to_objects = self.compute_objects(
            body['wallMaterial'], body['wallColors'])
        for tag in self._tag_to_objects:
            for object_instance in self._tag_to_objects[tag]:
                object_instance['role'] = tag

        body['performerStart'] = self._performer_start
        body['objects'] = [element for value in self._tag_to_objects.values()
                           for element in value]
        body['goal'] = self._get_config(self._tag_to_objects)

        if find_path:
            body['answer']['actions'] = self._find_optimal_path(
                self._tag_to_objects['target'], body['objects'])

        return body

    def _compute_performer_start(self) -> Dict[str, Dict[str, float]]:
        """Compute the starting location (position & rotation) for the performer. Must return the same thing on
        multiple calls. This default implementation chooses a random location."""
        if self._performer_start is None:
            self._performer_start = {
                'position': {
                    'x': round(random.uniform(
                        geometry.ROOM_X_MIN + util.PERFORMER_HALF_WIDTH,
                        geometry.ROOM_X_MAX - util.PERFORMER_HALF_WIDTH
                    ), geometry.POSITION_DIGITS),
                    'y': 0,
                    'z': round(random.uniform(
                        geometry.ROOM_Z_MIN + util.PERFORMER_HALF_WIDTH,
                        geometry.ROOM_Z_MAX - util.PERFORMER_HALF_WIDTH
                    ), geometry.POSITION_DIGITS)
                },
                'rotation': {
                    'x': 0,
                    'y': geometry.random_rotation(),
                    'z': 0
                }
            }
        return self._performer_start

    @abstractmethod
    def compute_objects(self, wall_material_name: str,
                        wall_colors: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """Compute object instances for the scene. Returns a tuple:
        (dict that maps tag strings to object lists, bounding rectangles)"""
        pass

    def update_goal_info_list(self,
                              info_list: List[str],
                              tag_to_objects: Dict[str,
                                                   List[Dict[str,
                                                             Any]]]) -> List[str]:
        """Update and return the given info_list with the info from all objects in this goal."""
        info_set = set(info_list)
        for key, value in tag_to_objects.items():
            for obj in value:
                info_list = obj.get('info', []).copy()
                if 'goalString' in obj:
                    info_list.append(obj['goalString'])
                info_set |= set([(key + ' ' + info) for info in info_list])
        return list(info_set)

    def _get_config(
            self, tag_to_objects: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Create and return the goal configuration."""
        goal_config = self._get_subclass_config(tag_to_objects['target'])
        goal_config['category'] = goal_config.get('category', '')
        goal_config['type_list'] = tags.append_object_tags(
            goal_config.get('type_list', []), tag_to_objects)
        goal_config['info_list'] = self.update_goal_info_list(
            goal_config.get('info_list', []), tag_to_objects)
        goal_config['metadata'] = goal_config.get('metadata', {})
        return goal_config

    def get_name(self) -> str:
        """Returns the name of this goal."""
        return self._name

    def get_performer_start(self) -> Dict[str, float]:
        """Returns the performer start."""
        return self._performer_start

    def reset_performer_start(self) -> Dict[str, float]:
        """Resets the performer start and returns the new performer start."""
        self._performer_start = None
        self._compute_performer_start()
        return self._performer_start

    @abstractmethod
    def _get_subclass_config(
            self, goal_objects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get the goal configuration of this specific subclass."""
        pass

    @abstractmethod
    def _find_optimal_path(self,
                           goal_objects: List[Dict[str,
                                                   Any]],
                           all_objects: List[Dict[str,
                                                  Any]]) -> List[Dict[str,
                                                                      Any]]:
        """Compute the optimal set of moves and update the body object"""
        pass


class EmptyGoal(Goal):
    """An empty goal."""

    def __init__(self):
        super(EmptyGoal, self).__init__()

    def compute_objects(self, wall_material_name: str,
                        wall_colors: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        return {'target': []}

    def _get_subclass_config(
            self, goal_objects: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {}

    def _find_optimal_path(self,
                           goal_objects: List[Dict[str,
                                                   Any]],
                           all_objects: List[Dict[str,
                                                  Any]]) -> List[Dict[str,
                                                                      Any]]:
        return []
