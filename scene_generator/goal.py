import logging
import random
import uuid
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, List, Optional

import exceptions
import geometry
import objects
import separating_axis_theorem
import util

MAX_WALL_WIDTH = 4
MIN_WALL_WIDTH = 1
WALL_Y_POS = 1.5
WALL_HEIGHT = 3
WALL_DEPTH = 0.1
MAX_OBJECTS = 5
WALL_COUNTS = [0, 1, 2, 3]
WALL_PROBS = [60, 20, 10, 10]

MAX_PAINTING_WIDTH = 1.5
MIN_PAINTING_WIDTH = 0.5
PAINTING_DEPTH = 0.05

DIST_WALL_APART = 1
SAFE_DIST_FROM_ROOM_WALL = 3.5
    

def generate_wall(wall_material: str, wall_colors: List[str], performer_position: Dict[str, float],
                  other_rects: List[List[Dict[str, float]]]) -> Optional[Dict[str, Any]]:
    # Wanted to reuse written functions, but this is a bit more of a special snowflake
    # Generates obstacle walls placed in the scene.

    tries = 0
    performer_rect = geometry.find_performer_rect(performer_position)
    performer_poly = geometry.rect_to_poly(performer_rect)
    while tries < util.MAX_TRIES:
        rotation = random.choice((0, 90, 180, 270))
        new_x = geometry.random_position()
        new_z = geometry.random_position()
        new_x_size = round(random.uniform(MIN_WALL_WIDTH, MAX_WALL_WIDTH), geometry.POSITION_DIGITS)
        
        # Make sure the wall is not too close to the rooms 4 walls
        if ((rotation == 0 or rotation == 180) and (new_z < -SAFE_DIST_FROM_ROOM_WALL or new_z > SAFE_DIST_FROM_ROOM_WALL)) or \
            ((rotation == 90 or rotation == 270) and (new_x < -SAFE_DIST_FROM_ROOM_WALL or new_x > SAFE_DIST_FROM_ROOM_WALL)): 
            continue
        else:
            rect = geometry.calc_obj_coords(new_x, new_z, 0, new_x_size, WALL_DEPTH, 0, 0, rotation)
            # barrier_rect is to allow parallel walls to be at least 1(DIST_WALL_APART) apart on the appropriate axis
            barrier_rect = geometry.calc_obj_coords(new_x, new_z, 0, new_x_size + DIST_WALL_APART, WALL_DEPTH + DIST_WALL_APART, 0, 0, rotation)
            wall_poly = geometry.rect_to_poly(rect)
            if not wall_poly.intersects(performer_poly) and \
                    geometry.rect_within_room(rect) and \
                    (len(other_rects) == 0 or not any(separating_axis_theorem.sat_entry(barrier_rect, other_rect) for other_rect in other_rects)): 
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

#TODO:
def generate_painting(painting_material: str, wall_colors: List[str], performer_position: Dict[str, float],
                  other_rects: List[List[Dict[str, float]]], generated_wall_rects: List[List[Dict[str, float]]]) -> Optional[Dict[str, Any]]:
    # Chance to generate a painting in the room, that can only be hanged on a wall

    # 1) Randomly grab x,y,z coordinate like generate_walls 
    # 2) Make sure painting(to be generated) is close to any wall 
    # 3) Make sure the painting is not intersecting any objects, is within the room
    # 4) Create the painting if it is valid

    # First goal- Make sure I can generate a painting(mini-wall) won any of the rooms 4 walls
    # Second goal- make sure I can generate a painting on generated_walls()

    tries = 0
    performer_rect = geometry.find_performer_rect(performer_position)
    performer_poly = geometry.rect_to_poly(performer_rect)
    while tries < util.MAX_TRIES:
        rotation = random.choice((0, 90, 180, 270))
        new_x = geometry.random_position()
        new_z = geometry.random_position()
        new_y = geometry.random_position()
        new_x_size = round(random.uniform(MIN_PAINTING_WIDTH, MAX_PAINTING_WIDTH), geometry.POSITION_DIGITS)
        painting_height = round(random.uniform(MIN_PAINTING_WIDTH, MAX_PAINTING_WIDTH), geometry.POSITION_DIGITS)


        if (((rotation == 0 or rotation == 180) and (new_z < -SAFE_DIST_FROM_ROOM_WALL or new_z > SAFE_DIST_FROM_ROOM_WALL)) or \
            ((rotation == 90 or rotation == 270) and (new_x < -SAFE_DIST_FROM_ROOM_WALL or new_x > SAFE_DIST_FROM_ROOM_WALL))) and \
           (new_y > 0.5 and new_y + painting_height + 0.03 < SAFE_DIST_FROM_ROOM_WALL): # Don't want painting going thru floor && ceiling

            cur_painting_obj = dict()
            shows_object = {'bounding_box': geometry.calc_obj_coords(new_x, new_z, new_y, new_x_size, PAINTING_DEPTH, 0, 0, rotation)}
            cur_painting_obj['shows'] = [shows_object]
            temp_rect = geometry.calc_obj_coords(new_x, new_z, new_y, new_x_size, PAINTING_DEPTH, 0, 0, rotation)
            adj_to_generated_wall = False
            if (rotation == 0 or rotation == 180): #Make sure the painting is on the wall, instead of hovering in front of the wall
                
                for wall in generated_wall_rects:  #first check if painting is near any generated wall, that can be placed on
                    left_z_boundary = wall['shows'][0]['bounding_box'][2]['z'] #wall['shows'][0]['position']['z']
                    right_z_boundary = wall['shows'][0]['bounding_box'][0]['z'] #wall['shows'][0]['position']['z'] +  wall['shows'][0]['scale']['x']
                    print("left:", left_z_boundary)
                    print("temp left:", temp_rect[2]['z'])

                    if (wall['shows'][0]['rotation']['y'] == 0 or wall['shows'][0]['rotation']['y'] == 180) and \
                        geometry.are_adjacent(wall, cur_painting_obj, 0.3) and \
                        left_z_boundary <= temp_rect[2]['z'] and right_z_boundary >= temp_rect[0]['z']:
                        adj_to_generated_wall = True
                        print("GGGGGGGGGGGG")
                        break

                if not adj_to_generated_wall: #Place near 1 of the 4 room walls
                    if new_z < 0:
                        new_z = geometry.ROOM_DIMENSIONS[1][0] - 0.03 
                    else:
                        new_z = geometry.ROOM_DIMENSIONS[1][1] + 0.03 
            elif (rotation == 90 or rotation == 270):

                for wall in generated_wall_rects:
                    left_x_boundary = wall['shows'][0]['bounding_box'][3]['x'] #wall['shows'][0]['position']['z']
                    right_x_boundary = wall['shows'][0]['bounding_box'][1]['x'] #wall['shows'][0]['position']['z'] +  wall['shows'][0]['scale']['x']

                    if (wall['shows'][0]['rotation']['y'] == 90 or wall['shows'][0]['rotation']['y'] == 270) and \
                        geometry.are_adjacent(wall, cur_painting_obj, 0.3) and \
                        left_x_boundary <= temp_rect[3]['x'] and right_x_boundary >= temp_rect[1]['x']:
                        adj_to_generated_wall = True
                        print("GGGGGGGGGGGG22222")
                        break
                
                if not adj_to_generated_wall:
                    if new_x < 0:
                        new_x = geometry.ROOM_DIMENSIONS[0][0] - 0.03 
                    else:
                        new_x = geometry.ROOM_DIMENSIONS[0][1] + 0.03 


            rect = geometry.calc_obj_coords(new_x, new_z, new_y, new_x_size, PAINTING_DEPTH, 0, 0, rotation)
            painting_poly = geometry.rect_to_poly(rect)
            if not painting_poly.intersects(performer_poly) and \
                    (len(other_rects) == 0 or not any(separating_axis_theorem.sat_entry(rect, other_rect) for other_rect in other_rects)): 
                break

        tries += 1
    
    if tries < util.MAX_TRIES:
        new_object = {
            'id': 'painting_' + str(uuid.uuid4()), 
            'materials': [painting_material],
            'type': 'cube',
            'kinematic': 'true',
            'structure': 'true',
            'mass': 100,
            'info': wall_colors,
            'info_string': ' '.join(wall_colors)
        }
        shows_object = {
            'stepBegin': 0,
            'scale': {'x': new_x_size, 'y': painting_height, 'z': PAINTING_DEPTH},
            'rotation': {'x': 0, 'y': rotation, 'z': 0},
            'position': {'x': new_x, 'y': new_y, 'z': new_z},
            'bounding_box': rect
        }
        shows = [shows_object]
        new_object['shows'] = shows

        return new_object

    return None


class Goal(ABC):
    """An abstract Goal. Subclasses must implement compute_objects and
    get_config. Users of a goal object should normally only need to call 
    update_body."""

    def __init__(self):
        self._performer_start = None
        self._targets = []
        self._tag_to_objects = []

    def update_body(self, body: Dict[str, Any], find_path: bool) -> Dict[str, Any]:
        """Helper method that calls other Goal methods to set performerStart, objects, and goal. Returns the goal body
        object."""
        body['performerStart'] = self.compute_performer_start()

        tag_to_objects, bounding_rects = self.compute_objects(body['wallMaterial'])
        self._tag_to_objects = tag_to_objects
        self._targets = tag_to_objects['target']

        walls = self.generate_walls(body['wallMaterial'], body['wallColors'], body['performerStart']['position'], bounding_rects)
        #print("walls: ", walls)
        for wall in walls:
            bounding_rects.append(wall['shows'][0]['bounding_box'])

        paintings = self.generate_paintings(body['paintingMaterial'], body['paintingColors'], body['performerStart']['position'], bounding_rects, walls)
        #print("paintings: ", paintings)
        print("hit")
        print("\n\n\n")

        walls.extend(paintings) #FIXME: need to have seperate tag for paintings
        
        if walls is not None:
            tag_to_objects['wall'] = walls
        #if paintings:
            #tag_to_objects['paintings'] = paintings
        

        body['objects'] = [element for value in tag_to_objects.values() for element in value]
        body['goal'] = self.get_config(self._targets, tag_to_objects)

        if find_path:
            body['answer']['actions'] = self.find_optimal_path(self._targets, body['objects'])

        return body

    def compute_performer_start(self) -> Dict[str, Dict[str, float]]:
        """Compute the starting location (position & rotation) for the performer. Must return the same thing on
        multiple calls. This default implementation chooses a random location."""
        if self._performer_start is None:
            self._performer_start = {
                'position': {
                    'x': geometry.random_position(),
                    'y': 0,
                    'z': geometry.random_position()
                },
                'rotation': {
                    'y': geometry.random_rotation()
                }
            }
        return self._performer_start

    def choose_object_def(self) -> Dict[str, Any]:
        """Pick one object definition (to be added to the scene) and return a copy of it."""
        object_def_list = random.choices([objects.OBJECTS_PICKUPABLE, objects.OBJECTS_MOVEABLE,
                                          objects.OBJECTS_IMMOBILE],
                                         [50, 25, 25])[0]
        return util.finalize_object_definition(random.choice(object_def_list))

    @abstractmethod
    def compute_objects(self, wall_material_name: str) -> \
            Tuple[Dict[str, List[Dict[str, Any]]], List[List[Dict[str, float]]]]:
        """Compute object instances for the scene. Returns a tuple:
        (dict that maps tag strings to object lists, bounding rectangles)"""
        pass

    def add_objects(self, object_list: List[Dict[str, Any]], rectangles: List[List[Dict[str, float]]],
                    performer_position: Dict[str, float]) -> None:
        """Add random objects to fill object_list to some random number of objects up to MAX_OBJECTS. If object_list
        already has more than this randomly determined number, no new objects are added."""
        object_count = random.randint(1, MAX_OBJECTS)
        for i in range(len(object_list), object_count):
            object_def = self.choose_object_def()
            obj_location = geometry.calc_obj_pos(performer_position, rectangles, object_def)
            obj_info = object_def['info'][-1]
            targets_info = [tgt['info'][-1] for tgt in self._targets]
            if obj_info not in targets_info and obj_location is not None:
                obj = util.instantiate_object(object_def, obj_location)
                object_list.append(obj)

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
        if 'distractor' in tag_to_objects:
            self._update_goal_tags_of_type(goal, tag_to_objects['distractor'], 'distractor')

        goal['type_list'] = []
        for item in ['background object', 'distractor', 'occluder', 'target', 'wall']:
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

    def get_config(self, goal_objects: List[Dict[str, Any]], tag_to_objects: Dict[str, List[Dict[str, Any]]]) -> \
            Dict[str, Any]:
        """Get the goal configuration. goal_objects is the objects required for the goal (as returned from
        compute_objects)."""
        goal_config = self._get_subclass_config(goal_objects)
        self._update_goal_tags(goal_config, tag_to_objects)
        return goal_config

    @abstractmethod
    def _get_subclass_config(self, goal_objects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get the goal configuration of this specific subclass."""
        pass

    def generate_walls(self, material: str, colors: List[str], performer_position: Dict[str, Any],
                       bounding_rects: List[List[Dict[str, float]]]) -> List[Dict[str, Any]]:
        wall_count = 3 #random.choices(WALL_COUNTS, weights=WALL_PROBS, k=1)[0]
        
        walls = [] 
        # Add bounding rects to walls
        all_bounding_rects = [bounding_rect.copy() for bounding_rect in bounding_rects] 
        for x in range(0, wall_count):
            wall = generate_wall(material, colors, performer_position, all_bounding_rects)

            if wall is not None:
                walls.append(wall)
                all_bounding_rects.append(wall['shows'][0]['bounding_box'])
            else:
                logging.warning('could not generate wall')
        return walls

    def generate_paintings(self, material: str, colors: List[str], performer_position: Dict[str, Any],
                       bounding_rects: List[List[Dict[str, float]]], wall_bounding_rects=None) -> List[Dict[str, Any]]:
        painting_count = 3 #random.choices(WALL_COUNTS, weights=WALL_PROBS, k=1)[0] # Using same probability as walls

        paintings = []
        all_bounding_rects = [bounding_rect.copy() for bounding_rect in bounding_rects]
        for x in range(0, painting_count):
            painting = generate_painting(material, colors, performer_position, all_bounding_rects, wall_bounding_rects)

            if painting is not None:
                paintings.append(painting)
                all_bounding_rects.append(painting['shows'][0]['bounding_box'])
            else:
                logging.warning('could not generate painting')
        return paintings
    

    @abstractmethod
    def find_optimal_path(self, goal_objects: List[Dict[str, Any]], all_objects: List[Dict[str, Any]]) -> \
            List[Dict[str, Any]]:
        """Compute the optimal set of moves and update the body object"""
        pass


class EmptyGoal(Goal):
    """An empty goal."""

    def __init__(self):
        super(EmptyGoal, self).__init__()

    def compute_objects(self, wall_material_name: str) -> \
            Tuple[Dict[str, List[Dict[str, Any]]], List[List[Dict[str, float]]]]:
        return { 'target': [] }, []

    def _get_subclass_config(self, goal_objects: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {}

    def find_optimal_path(self, goal_objects: List[Dict[str, Any]], all_objects: List[Dict[str, Any]]) -> \
            List[Dict[str, Any]]:
        return []


class GoalException(exceptions.SceneException):
    def __init__(self, message=''):
        super(GoalException, self).__init__(message)
