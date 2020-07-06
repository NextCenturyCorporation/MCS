import logging
import random
import shapely
import uuid
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, List, Optional

import geometry
import objects
import separating_axis_theorem
import util

MAX_WALL_WIDTH = 4
MIN_WALL_WIDTH = 1
WALL_Y_POS = 1.5
WALL_HEIGHT = 3
WALL_DEPTH = 0.1

DIST_WALL_APART = 1
SAFE_DIST_FROM_ROOM_WALL = 3.5
    

def generate_wall(wall_material: str, wall_colors: List[str], performer_position: Dict[str, float], \
        other_rects: List[List[Dict[str, float]]], target_list: List[Dict[str, Any]] = None) -> \
        Optional[Dict[str, Any]]:
    """Generates and returns a randomly positioned obstacle wall. If target_list is not None, the wall won't obstruct
    the line between the performer_position and the target_list."""

    tries = 0
    performer_rect = geometry.find_performer_rect(performer_position)
    performer_poly = geometry.rect_to_poly(performer_rect)
    while tries < util.MAX_TRIES:
        rotation = random.choice((0, 90, 180, 270))
        new_x = geometry.random_position_x()
        new_z = geometry.random_position_z()
        new_x_size = round(random.uniform(MIN_WALL_WIDTH, MAX_WALL_WIDTH), geometry.POSITION_DIGITS)
        
        # Make sure the wall is not too close to the rooms 4 walls
        if ((rotation == 0 or rotation == 180) and (new_z < -SAFE_DIST_FROM_ROOM_WALL or new_z > SAFE_DIST_FROM_ROOM_WALL)) or \
            ((rotation == 90 or rotation == 270) and (new_x < -SAFE_DIST_FROM_ROOM_WALL or new_x > SAFE_DIST_FROM_ROOM_WALL)): 
            continue

        rect = geometry.calc_obj_coords(new_x, new_z, new_x_size, WALL_DEPTH, 0, 0, rotation)
        # barrier_rect is to allow parallel walls to be at least 1(DIST_WALL_APART) apart on the appropriate axis
        barrier_rect = geometry.calc_obj_coords(new_x, new_z, new_x_size + DIST_WALL_APART, WALL_DEPTH + DIST_WALL_APART, 0, 0, rotation)
        wall_poly = geometry.rect_to_poly(rect)
        is_ok = not wall_poly.intersects(performer_poly) and geometry.rect_within_room(rect) and \
                (len(other_rects) == 0 or not any(separating_axis_theorem.sat_entry(barrier_rect, other_rect) \
                for other_rect in other_rects))
        if is_ok:
            if target_list:
                for target in target_list:
                    if geometry.does_obstruct_target(performer_position, target, wall_poly):
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
            'mass': 100,
            'info': wall_colors,
            'info_string': ' '.join(wall_colors)
        }
        shows_object = {
            'stepBegin': 0,
            'scale': {'x': new_x_size, 'y': WALL_HEIGHT, 'z': WALL_DEPTH},
            'rotation': {'x': 0, 'y': rotation, 'z': 0},
            'position': {'x': new_x, 'y': WALL_Y_POS, 'z': new_z},
            'bounding_box': rect
        }
        shows = [shows_object]
        new_object['shows'] = shows

        return new_object
    return None


def generate_painting(painting_material: str, performer_position: Dict[str, float],
                  other_rects: List[List[Dict[str, float]]]) -> Optional[Dict[str, Any]]:
    # Chance to generate a painting in the room, that can only be hanged on a wall

    # 1) Randomly grab x,y,z coordinate like generate_walls 
    # 2) Make sure painting(to be generated) is close to any wall 
    # 3) Make sure the painting is not intersecting any objects, is within the room
    # 4) Create the painting if it is valid

    print('Make paintings')

    return None
    

class Goal(ABC):
    """An abstract Goal. Subclasses must implement compute_objects and
    get_config. Users of a goal object should normally only need to call 
    update_body."""

    def __init__(self, name: str):
        self._name = name
        self._performer_start = None
        self._compute_performer_start()
        self._tag_to_objects = []

    def update_body(self, body: Dict[str, Any], find_path: bool) -> Dict[str, Any]:
        """Helper method that calls other Goal methods to set performerStart, objects, and goal. Returns the goal body
        object."""
        self._tag_to_objects = self.compute_objects(body['wallMaterial'], body['wallColors'])

        body['performerStart'] = self._performer_start
        body['objects'] = [element for value in self._tag_to_objects.values() for element in value]
        body['goal'] = self.get_config(self._tag_to_objects)

        if find_path:
            body['answer']['actions'] = self._find_optimal_path(self._tag_to_objects['target'], body['objects'])

        return body

    def _compute_performer_start(self) -> Dict[str, Dict[str, float]]:
        """Compute the starting location (position & rotation) for the performer. Must return the same thing on
        multiple calls. This default implementation chooses a random location."""
        if self._performer_start is None:
            self._performer_start = {
                'position': {
                    'x': round(random.uniform(
                        geometry.ROOM_DIMENSIONS[0][0] + util.PERFORMER_HALF_WIDTH,
                        geometry.ROOM_DIMENSIONS[0][1] - util.PERFORMER_HALF_WIDTH
                    ), geometry.POSITION_DIGITS),
                    'y': 0,
                    'z': round(random.uniform(
                        geometry.ROOM_DIMENSIONS[1][0] + util.PERFORMER_HALF_WIDTH,
                        geometry.ROOM_DIMENSIONS[1][1] - util.PERFORMER_HALF_WIDTH
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
    def compute_objects(self, wall_material_name: str, wall_colors: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """Compute object instances for the scene. Returns a tuple:
        (dict that maps tag strings to object lists, bounding rectangles)"""
        pass

    def _update_goal_info_list(self, goal: Dict[str, Any], tag_to_objects: Dict[str, List[Dict[str, Any]]]) -> None:
        info_set = set(goal.get('info_list', []))

        for key, value in tag_to_objects.items():
            for obj in value:
                info_list = obj.get('info', []).copy()
                if 'info_string' in obj:
                    info_list.append(obj['info_string'])
                info_set |= set([(key + ' ' + info) for info in info_list])

        goal['info_list'] = list(info_set)

    def _update_goal_tags(self, goal: Dict[str, Any], tag_to_objects: Dict[str, List[Dict[str, Any]]]) -> None:
        self._update_goal_tags_of_type(goal, tag_to_objects['target'], 'target')
        if 'confusor' in tag_to_objects:
            self._update_goal_tags_of_type(goal, tag_to_objects['confusor'], 'confusor')
        if 'distractor' in tag_to_objects:
            self._update_goal_tags_of_type(goal, tag_to_objects['distractor'], 'distractor')
        if 'obstructor' in tag_to_objects:
            self._update_goal_tags_of_type(goal, tag_to_objects['obstructor'], 'obstructor')
        for item in ['background object', 'confusor', 'distractor', 'obstructor', 'occluder', 'target', 'wall']:
            if item in tag_to_objects:
                number = len(tag_to_objects[item])
                if item == 'occluder':
                    number = (int)(number / 2)
                goal['type_list'].append(item + 's ' + str(number))
        self._update_goal_info_list(goal, tag_to_objects)

    def _update_goal_tags_of_type(self, goal: Dict[str, Any], objs: List[Dict[str, Any]], name: str) -> None:
        for obj in objs:
            enclosed_tag = (name + ' not enclosed') if obj.get('locationParent', None) is None else (name + ' enclosed')
            novel_color_tag = (name + ' novel color') if 'novel_color' in obj and obj['novel_color'] else \
                    (name + ' not novel color')
            novel_combination_tag = (name + ' novel combination') if 'novel_combination' in obj and \
                    obj['novel_combination'] else (name + ' not novel combination')
            novel_shape_tag = (name + ' novel shape') if 'novel_shape' in obj and obj['novel_shape'] else \
                    (name + ' not novel shape')
            for new_tag in [enclosed_tag, novel_color_tag, novel_combination_tag, novel_shape_tag]:
                if new_tag not in goal['type_list']:
                    goal['type_list'].append(new_tag)

    def get_config(self, tag_to_objects: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Create and return the goal configuration."""
        goal_config = self._get_subclass_config(tag_to_objects['target'])
        self._update_goal_tags(goal_config, tag_to_objects)
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
    def _get_subclass_config(self, goal_objects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get the goal configuration of this specific subclass."""
        pass

    @abstractmethod
    def _find_optimal_path(self, goal_objects: List[Dict[str, Any]], all_objects: List[Dict[str, Any]]) -> \
            List[Dict[str, Any]]:
        """Compute the optimal set of moves and update the body object"""
        pass


class EmptyGoal(Goal):
    """An empty goal."""

    def __init__(self):
        super(EmptyGoal, self).__init__()

    def compute_objects(self, wall_material_name: str, wall_colors: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        return { 'target': [] }

    def _get_subclass_config(self, goal_objects: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {}

    def _find_optimal_path(self, goal_objects: List[Dict[str, Any]], all_objects: List[Dict[str, Any]]) -> \
            List[Dict[str, Any]]:
        return []

