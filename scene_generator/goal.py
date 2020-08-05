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

MAX_PAINTING_WIDTH = 1.5
MIN_PAINTING_WIDTH = 0.5
MAX_PAINTING_HEIGHT = 1.5
MIN_PAINTING_HEIGHT = 0.5
PAINTING_DEPTH = 0.05

DIST_WALL_APART = 1
SAFE_DIST_FROM_ROOM_WALL = 3.5
SAFE_DIST_FROM_CENTER_OF_PAINTING_AND_GENERATED_WALL = 0.3
    

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
        """
        if ((rotation == 0 or rotation == 180) and (new_z < -SAFE_DIST_FROM_ROOM_WALL or new_z > SAFE_DIST_FROM_ROOM_WALL)) or \
            ((rotation == 90 or rotation == 270) and (new_x < -SAFE_DIST_FROM_ROOM_WALL or new_x > SAFE_DIST_FROM_ROOM_WALL)): 
            continue
        """
        if (new_z < -SAFE_DIST_FROM_ROOM_WALL or new_z > SAFE_DIST_FROM_ROOM_WALL) or \
            (new_x < -SAFE_DIST_FROM_ROOM_WALL or new_x > SAFE_DIST_FROM_ROOM_WALL):
            continue

        rect = geometry.calc_obj_coords(new_x, new_z, new_x_size, WALL_DEPTH, 0, 0, rotation, position_y=0)
        # barrier_rect is to allow parallel walls to be at least 1(DIST_WALL_APART) apart on the appropriate axis
        barrier_rect = geometry.calc_obj_coords(new_x, new_z, new_x_size + DIST_WALL_APART, WALL_DEPTH + DIST_WALL_APART, 0, 0, rotation, position_y=0)
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
        new_x = geometry.random_position_x()
        new_z = geometry.random_position_z()
        new_y = geometry.random_position_y()
        new_x_size = round(random.uniform(MIN_PAINTING_WIDTH, MAX_PAINTING_WIDTH), geometry.POSITION_DIGITS)
        painting_height = round(random.uniform(MIN_PAINTING_HEIGHT, MAX_PAINTING_HEIGHT), geometry.POSITION_DIGITS)

        #TODO: add if statments 
        doesnt_intersect_sides = (new_x - new_x_size > geometry.ROOM_DIMENSIONS[0][0]) and (new_x + new_x_size < geometry.ROOM_DIMENSIONS[0][1])
        doesnt_intersect_sides2 = (new_z - new_x_size > geometry.ROOM_DIMENSIONS[1][0]) and (new_z + new_x_size < geometry.ROOM_DIMENSIONS[1][1])

        if (new_z > -SAFE_DIST_FROM_ROOM_WALL and new_z < SAFE_DIST_FROM_ROOM_WALL) and \
            (new_x > -SAFE_DIST_FROM_ROOM_WALL and new_x < SAFE_DIST_FROM_ROOM_WALL) and \
            (new_y > 1 and new_y + painting_height + 0.03 < SAFE_DIST_FROM_ROOM_WALL):

            adj_to_generated_wall = False
            bounding_rect = dict()

            for wall in generated_wall_rects:

                if (wall['shows'][0]['rotation']['y'] == 0 or wall['shows'][0]['rotation']['y'] == 180) and \
                    (rotation == 0 or rotation == 180):

                    x_list = [coord['x'] for coord in wall['shows'][0]['bounding_box']]
                    x_list.sort()
                    left_x_boundary = x_list[0]
                    right_x_boundary = x_list[3] 

                    new_z = wall['shows'][0]['position']['z'] + random.choice([WALL_DEPTH - 0.03, -WALL_DEPTH + 0.03]) # FIXME Test to see paintings on generated wall
                    
                    bounding_rect['bounding_box'] = geometry.calc_obj_coords(new_x, new_z, new_x_size, PAINTING_DEPTH, 0, 0, rotation, position_y=new_y)
                    
                    painting_x_list = [coord['x'] for coord in bounding_rect['bounding_box']]
                    painting_x_list.sort()
                    painting_left_x_boundary = painting_x_list[0]
                    painting_right_x_boundary = painting_x_list[3]

                    if geometry.are_adjacent(wall, bounding_rect, 0.1) and \
                        (abs(new_x - wall['shows'][0]['position']['x']) < SAFE_DIST_FROM_CENTER_OF_PAINTING_AND_GENERATED_WALL) and \
                        left_x_boundary <= painting_left_x_boundary and right_x_boundary >= painting_right_x_boundary: 

                        adj_to_generated_wall = True
                        print("x left bound:", left_x_boundary, " |x right bound:", right_x_boundary)
                        print("painting x left:", painting_left_x_boundary, "|painting x right:", painting_right_x_boundary)
                        #print("z val:", new_z)
                        print("wall rect",  wall['shows'][0]['bounding_box'])
                        print("painting rect:", bounding_rect['bounding_box'])
                        break
                
                elif (wall['shows'][0]['rotation']['y'] == 90 or wall['shows'][0]['rotation']['y'] == 270) and \
                     (rotation == 90 or rotation == 270):

                    z_list = [coord['z'] for coord in wall['shows'][0]['bounding_box']]
                    z_list.sort()
                    left_z_boundary = z_list[0]
                    right_z_boundary = z_list[3]

                    new_x = wall['shows'][0]['position']['x'] + random.choice([WALL_DEPTH - 0.03, -WALL_DEPTH + 0.03]) # FIXME Test to see paintings on generated wall
                    
                    bounding_rect['bounding_box'] = geometry.calc_obj_coords(new_x, new_z, new_x_size, PAINTING_DEPTH, 0, 0, rotation, position_y=new_y)
                    
                    painting_z_list = [coord['z'] for coord in bounding_rect['bounding_box']] 
                    painting_z_list.sort()
                    painting_left_z_boundary = painting_z_list[0]
                    painting_right_z_boundary = painting_z_list[3]

                    if geometry.are_adjacent(wall, bounding_rect, 0.1) and \
                        (abs(new_z - wall['shows'][0]['position']['z']) < SAFE_DIST_FROM_CENTER_OF_PAINTING_AND_GENERATED_WALL) and \
                        left_z_boundary <= painting_left_z_boundary and right_z_boundary >= painting_right_z_boundary: 

                        adj_to_generated_wall = True
                        print("z left bound:", left_z_boundary, " |z right bound:", right_z_boundary)
                        print("painting z left:", painting_left_z_boundary, "|painting z right:", painting_right_z_boundary)
                        #print("x val:", new_x)
                        print("wall rect",  wall['shows'][0]['bounding_box'])
                        print("painting rect:", bounding_rect['bounding_box'])
                        break

            if (rotation == 0 or rotation == 180) and not adj_to_generated_wall:  #Place near 1 of the 4 room walls
                if new_z < 0:
                    new_z = geometry.ROOM_DIMENSIONS[1][0] - 0.03 
                else:
                    new_z = geometry.ROOM_DIMENSIONS[1][1] + 0.03 
            elif (rotation == 90 or rotation == 270) and not adj_to_generated_wall:
                if new_x < 0:
                    new_x = geometry.ROOM_DIMENSIONS[0][0] - 0.03 
                else:
                    new_x = geometry.ROOM_DIMENSIONS[0][1] + 0.03 

            rect = geometry.calc_obj_coords(new_x, new_z, new_x_size, PAINTING_DEPTH, 0, 0, rotation, position_y=new_y)
            painting_poly = geometry.rect_to_poly(rect)

            if not painting_poly.intersects(performer_poly) and \
                    (len(other_rects) == 0 or not any(separating_axis_theorem.sat_entry(rect, other_rect) for other_rect in other_rects)): 
                break

        """
        if (((rotation == 0 or rotation == 180) and (new_z > -SAFE_DIST_FROM_ROOM_WALL and new_z < SAFE_DIST_FROM_ROOM_WALL) ) or \
            ((rotation == 90 or rotation == 270) and (new_x > -SAFE_DIST_FROM_ROOM_WALL and new_x < SAFE_DIST_FROM_ROOM_WALL))) and \
           (new_y > 0.7 and new_y + painting_height + 0.03 < SAFE_DIST_FROM_ROOM_WALL): # Don't want painting going thru floor && ceiling

            adj_to_generated_wall = False
            bounding_rect = dict()
            
            if (rotation == 0 or rotation == 180): #Make sure the painting is on the wall
        
                for wall in generated_wall_rects:
                    if wall['shows'][0]['rotation']['y'] == 0 or wall['shows'][0]['rotation']['y'] == 180:
                        
                        x_list = [coord['x'] for coord in wall['shows'][0]['bounding_box']]
                        x_list.sort()
                        left_x_boundary = x_list[0]
                        right_x_boundary = x_list[3] 

                        new_z = wall['shows'][0]['position']['z'] + random.choice([WALL_DEPTH - 0.03, -WALL_DEPTH + 0.03]) # FIXME Test to see paintings on generated wall
                        
                        bounding_rect['bounding_box'] = geometry.calc_obj_coords(new_x, new_z, new_x_size, PAINTING_DEPTH, 0, 0, rotation, position_y=new_y)
                        
                        painting_x_list = [coord['x'] for coord in bounding_rect['bounding_box']]
                        painting_x_list.sort()
                        painting_left_x_boundary = painting_x_list[0]
                        painting_right_x_boundary = painting_x_list[3]

                        if geometry.are_adjacent(wall, bounding_rect, 0.1) and \
                            left_x_boundary <= painting_left_x_boundary and right_x_boundary >= painting_right_x_boundary: 
                            adj_to_generated_wall = True
                            
                            print("x left bound:", left_x_boundary, " |x right bound:", right_x_boundary)
                            print("painting x left:", painting_left_x_boundary, "|painting x right:", painting_right_x_boundary)
                            #print("z val:", new_z)
                            print("wall rect",  wall['shows'][0]['bounding_box'])
                            print("painting rect:", bounding_rect['bounding_box'])
                            break

                if not adj_to_generated_wall: #Place near 1 of the 4 room walls
                    if new_z < 0:
                        new_z = geometry.ROOM_DIMENSIONS[1][0] - 0.03 
                    else:
                        new_z = geometry.ROOM_DIMENSIONS[1][1] + 0.03 

            elif (rotation == 90 or rotation == 270):
               
                for wall in generated_wall_rects:
                    if wall['shows'][0]['rotation']['y'] == 90 or wall['shows'][0]['rotation']['y'] == 270:

                        z_list = [coord['z'] for coord in wall['shows'][0]['bounding_box']]
                        z_list.sort()
                        left_z_boundary = z_list[0]
                        right_z_boundary = z_list[3]

                        new_x = wall['shows'][0]['position']['x'] + random.choice([WALL_DEPTH - 0.03, -WALL_DEPTH + 0.03]) # FIXME Test to see paintings on generated wall
                        
                        bounding_rect['bounding_box'] = geometry.calc_obj_coords(new_x, new_z, new_x_size, PAINTING_DEPTH, 0, 0, rotation, position_y=new_y)
                        
                        painting_z_list = [coord['z'] for coord in bounding_rect['bounding_box']] 
                        painting_z_list.sort()
                        painting_left_z_boundary = painting_z_list[0]
                        painting_right_z_boundary = painting_z_list[3]
                        
                        #print("old z:", wall['shows'][0]['position']['z'])

                        if geometry.are_adjacent(wall, bounding_rect, 0.1) and \
                            left_z_boundary <= painting_left_z_boundary and right_z_boundary >= painting_right_z_boundary: 
                            adj_to_generated_wall = True
                            
                            print("z left bound:", left_z_boundary, " |z right bound:", right_z_boundary)
                            print("painting z left:", painting_left_z_boundary, "|painting z right:", painting_right_z_boundary)
                            #print("x val:", new_x)
                            print("wall rect",  wall['shows'][0]['bounding_box'])
                            print("painting rect:", bounding_rect['bounding_box'])
                            break
                
                if not adj_to_generated_wall:
                    if new_x < 0:
                        new_x = geometry.ROOM_DIMENSIONS[0][0] - 0.03 
                    else:
                        new_x = geometry.ROOM_DIMENSIONS[0][1] + 0.03 


            rect = geometry.calc_obj_coords(new_x, new_z, new_x_size, PAINTING_DEPTH, 0, 0, rotation, position_y=new_y)
            painting_poly = geometry.rect_to_poly(rect)
            #if adj_to_generated_wall: # FIXME Testing
                #print("poly intersects:",not painting_poly.intersects(performer_poly))
                #print("other rects intersects:", (len(other_rects) == 0 or not any(separating_axis_theorem.sat_entry(rect, other_rect) for other_rect in other_rects)))

            if not painting_poly.intersects(performer_poly) and \
                    (len(other_rects) == 0 or not any(separating_axis_theorem.sat_entry(rect, other_rect) for other_rect in other_rects)): 
                break
        """

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

    def __init__(self, name: str=None):
        self._name = name
        self._performer_start = None
        self._compute_performer_start()
        self._tag_to_objects = []
        self._bounds_list = []

    def get_bounds_list(self) -> List[List[Dict[str, float]]]:
        """Returns the bounding rectangles of all objects in this goal."""
        return self._bounds_list

    def update_body(self, body: Dict[str, Any], find_path: bool) -> Dict[str, Any]:
        """Helper method that calls other Goal methods to set performerStart, objects, and goal. Returns the goal body
        object."""
        self._tag_to_objects = self.compute_objects(body['wallMaterial'], body['wallColors'])

        body['performerStart'] = self._performer_start
        walls = self.generate_walls(body['wallMaterial'], body['wallColors'], body['performerStart']['position'], [])
        
        #Create Walls for the rooms 4 bounding walls
        rooms_walls = [] 
        x_positions = [0, 0, 5.5, -5.5]
        z_positions = [5.5, -5.5, 0, 0]
        x_deltas = [1, 1, 1, 1]
        z_deltas = [1, 1, 1, 1]
        x_offsets = [0, 0, 0, 0]
        z_offsets = [0, 0, 0, 0]
        rotations = [0, 0, 90, 90]

        for i in range(0, 4):
            new_object = {
                'id': 'wall_' + str(uuid.uuid4()),
                'materials': [body['wallMaterial']],
                'type': 'cube',
                'kinematic': 'true',
                'structure': 'true',
                'mass': 100,
                'info': body['wallColors'],
                'info_string': ' '.join(body['wallColors'])
            }
            shows_object = {
                'stepBegin': 0,
                'scale': {'x': x_deltas[i], 'y': WALL_HEIGHT, 'z': z_deltas},
                'rotation': {'x': 0, 'y': rotations[i], 'z': 0},
                'position': {'x': x_positions[i], 'y': WALL_Y_POS, 'z': z_positions[i]},
                'bounding_box': geometry.calc_obj_coords(x_positions[i], z_positions[i], x_deltas[i], z_deltas[i], x_offsets[i], z_offsets[i], rotations[i])
            }
            new_object['shows'] = [shows_object]
            rooms_walls.append(new_object)
        
        all_walls = walls + rooms_walls #Messes up with generating a painting on a room wall
       
        paintings = self.generate_paintings(body['paintingMaterial'], body['paintingColors'], body['performerStart']['position'], self.get_bounds_list(), walls)
        print("hit")
        print("\n\n\n")
        
        if walls is not None:
            self._tag_to_objects['wall'] = walls

        if paintings:
            self._tag_to_objects['paintings'] = paintings

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
        goal['type_list'] = []
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

    def generate_walls(self, material: str, colors: List[str], performer_position: Dict[str, Any],
                       bounding_rects: List[List[Dict[str, float]]]) -> List[Dict[str, Any]]:
        wall_count = 3 #random.choices(WALL_COUNTS, weights=WALL_PROBS, k=1)[0] #FIXME want more walls to test
        
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
                       bounding_rects: List[List[Dict[str, float]]], wall_bounding_rects: List[List[Dict[str, float]]]=None) -> List[Dict[str, Any]]:
        painting_count = 3 #random.choices(WALL_COUNTS, weights=WALL_PROBS, k=1)[0] # Using same probability as walls #FIXME want more paintings to test

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

