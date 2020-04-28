#
# Goal generation
#

import copy
import logging
import random
import uuid
from abc import ABC, abstractmethod
from enum import Enum

import geometry
import materials
import objects
from geometry import random_position, random_rotation, calc_obj_pos, POSITION_DIGITS
from objects import OBJECTS_PICKUPABLE, OBJECTS_MOVEABLE, OBJECTS_IMMOBILE, OBJECTS_PICKUPABLE_LISTS
from separating_axis_theorem import sat_entry
from optimal_path import generatepath
from numpy.lib.scimath import sqrt
from numpy import degrees
from numpy.core import arctan2
import math

from machine_common_sense.mcs_controller_ai2thor import MAX_MOVE_DISTANCE

MAX_TRIES = 20
MAX_OBJECTS = 5
MAX_WALLS = 3
MIN_WALLS = 0
MAX_WALL_WIDTH = 4
MIN_WALL_WIDTH = 1
WALL_Y_POS = 1.5
WALL_HEIGHT = 3
WALL_DEPTH = 0.1
WALL_COUNTS = [0, 1, 2, 3]
WALL_PROBS = [60, 20, 10, 10]


def all_items_less_equal(a, b):
    """Return true iff every item in a is <= its corresponding item in b."""
    return all((a[key] <= b[key] for key in a))

def compute_acceleration(force, mass):
    """Return the acceleration imparted to mass by force (a x,y,z dictionary)"""
    accel = { item: force[item]/mass for item in force }
    return accel

def finalize_object_definition(object_def):
    object_def_copy = copy.deepcopy(object_def)

    # apply choice if necessary
    if 'choose' in object_def_copy:
        choice = random.choice(object_def_copy['choose'])
        for key in choice:
            object_def_copy[key] = choice[key]
        del object_def_copy['choose']

    return object_def_copy

def instantiate_object(object_def, object_location):
    """Create a new object from an object definition (as from the objects.json file). object_location will be modified
    by this function."""
    if object_def is None or object_location is None:
        raise ValueError('instantiate_object cannot take None parameters')

    # Call the finalize function here in case it wasn't called before now (calling it twice shouldn't hurt anything).
    object_def = finalize_object_definition(object_def)

    new_object = {
        'id': str(uuid.uuid4()),
        'type': object_def['type'],
        'info': object_def['info'],
        'mass': object_def['mass']
    }
    if 'dimensions' in object_def:
        new_object['dimensions'] = object_def['dimensions']
    else:
        logging.warning(f'object type "{object_def["type"]}" has no dimensions')

    for attribute in object_def['attributes']:
        new_object[attribute] = True

    if 'offset' in object_def:
        object_location['position']['x'] -= object_def['offset']['x']
        object_location['position']['z'] -= object_def['offset']['z']

    shows = [object_location]
    new_object['shows'] = shows
    object_location['stepBegin'] = 0
    object_location['scale'] = object_def['scale']
    colors = set()
    if 'materialCategory' in object_def:
        materials_list = [random.choice(getattr(materials, name.upper() + '_MATERIALS')) for name in
                          object_def['materialCategory']]
        new_object['materials'] = [mat[0] for mat in materials_list]
        for material in materials_list:
            for color in material[1]:
                colors.add(color)

    # specific ordering of adjectives for the info list:
    # size weight color(s) material(s) object
    info = object_def['info']
    if 'salientMaterials' in object_def:
        salient_materials = object_def['salientMaterials']
        new_object['salientMaterials'] = salient_materials
        info = info[:1] + salient_materials + info[1:]

    info = info[:1] + list(colors) + info[1:]

    if 'pickupable' in object_def['attributes']:
        size = 'light'
    elif 'moveable' in object_def['attributes']:
        size = 'heavy'
    else:
        size = 'massive'
    info = info[:1] + [size] + info[1:]

    info.append(' '.join(info))
    new_object['info'] = info
    return new_object


def move_to_container(target, all_objects, bounding_rects, performer_position):
    """Try to find a random container that target will fit in. If found, set the target's locationParent, and add
    container to all_objects (and bounding_rects). Return True iff the target was put in a container."""
    shuffled_containers = objects.get_enclosed_containers().copy()
    random.shuffle(shuffled_containers)
    for container_def in shuffled_containers:
        container_def = finalize_object_definition(container_def)
        area_index = geometry.can_contain(container_def, target)
        if area_index is not None:
            # try to place the container before we accept it
            container_location = geometry.calc_obj_pos(performer_position, bounding_rects, container_def)
            if container_location is not None:
                found_container = instantiate_object(container_def, container_location)
                found_area = container_def['enclosed_areas'][area_index]
                all_objects.append(found_container)
                target['locationParent'] = found_container['id']
                target['shows'][0]['position'] = found_area['position'].copy()
                target['shows'][0]['rotation'] = geometry.ORIGIN.copy()
                return True
    return False


def generate_wall(wall_mat_choice, performer_position, other_rects):
    # Wanted to reuse written functions, but this is a bit more of a special snowflake
    # Generates obstacle walls placed in the scene.

    tries = 0
    while tries < MAX_TRIES:
        rotation = random.choice((0, 90, 180, 270))
        new_x = random_position()
        new_z = random_position()
        new_x_size = round(random.uniform(MIN_WALL_WIDTH, MAX_WALL_WIDTH), POSITION_DIGITS)
        rect = geometry.calc_obj_coords(new_x, new_z, new_x_size, WALL_DEPTH, 0, 0, rotation)
        if not geometry.collision(rect, performer_position) and \
                all(geometry.point_within_room(point) for point in rect) and \
                (len(other_rects) == 0 or not any(sat_entry(rect, other_rect) for other_rect in other_rects)):
            break
        tries += 1

    if tries < MAX_TRIES:
        new_object = {
            'id': 'wall_' + str(uuid.uuid4()),
            'materials': [wall_mat_choice],
            'type': 'cube',
            'kinematic': 'true',
            'structure': 'true',
            'mass': 100
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


def generate_image_file_name(target):
    if 'materials' not in target:
        return target['type']

    material_name_list = [item[(item.rfind('/') + 1):].lower().replace(' ', '_') for item in target['materials']]
    return target['type'] + ('_' if len(material_name_list) > 0 else '') + ('_'.join(material_name_list))


def find_image_for_object(object_def):
    image_file_name = ""

    try:
        target_image = []
        image_file_name = 'images/' + generate_image_file_name(object_def) + '.txt'

        with open(image_file_name, 'r') as image_file:
            target_image = image_file.read()
            
        return target_image
    except: 
        logging.warning('Image object could not be found, make sure you generated the image: ' + image_file_name)


def find_image_name(target):
    return generate_image_file_name(target) + '.png'


class GoalException(Exception):
    def __init__(self, message=''):
        super(GoalException, self).__init__(message)


class Goal(ABC):
    """An abstract Goal. Subclasses must implement compute_objects and
    get_config. Users of a goal object should normally only need to call 
    update_body."""

    def __init__(self):
        self._performer_start = None
        self._targets = []

    def update_body(self, body, find_path):
        """Helper method that calls other Goal methods to set performerStart, objects, and goal. Returns the goal body
        object."""
        body['performerStart'] = self.compute_performer_start()
        goal_objects, all_objects, bounding_rects = self.compute_objects()
        walls = self.generate_walls(body['wallMaterial'], body['performerStart']['position'],
                                    bounding_rects)
        body['objects'] = all_objects + walls
        body['goal'] = self.get_config(goal_objects)
        if find_path:
            body['answer']['actions'] = self.find_optimal_path(goal_objects, all_objects+walls)
        
        return body

    def compute_performer_start(self):
        """Compute the starting location (position & rotation) for the performer. Must return the same thing on
        multiple calls. This default implementation chooses a random location."""
        if self._performer_start is None:
            self._performer_start = {
                'position': {
                    'x': random_position(),
                    'y': 0,
                    'z': random_position()
                },
                'rotation': {
                    'y': random_rotation()
                }
            }
        return self._performer_start

    def choose_object_def(self):
        """Pick one object definition (to be added to the scene) and return a copy of it."""
        object_def_list = random.choices([OBJECTS_PICKUPABLE, OBJECTS_MOVEABLE, OBJECTS_IMMOBILE],
                                         [50, 25, 25])[0]
        return finalize_object_definition(random.choice(object_def_list))

    @abstractmethod
    def compute_objects(self):
        """Compute object instances for the scene. Returns a tuple:
        (objects required for the goal, all objects in the scene including objects required for the goal, bounding rectangles)"""
        pass

    def add_objects(self, object_list, rectangles, performer_position):
        """Add random objects to fill object_list to some random number of objects up to MAX_OBJECTS. If object_list
        already has more than this randomly determined number, no new objects are added."""
        object_count = random.randint(1, MAX_OBJECTS)
        for i in range(len(object_list), object_count):
            object_def = self.choose_object_def()
            obj_location = calc_obj_pos(performer_position, rectangles, object_def)
            obj_info = object_def['info'][-1]
            targets_info = [tgt['info'][-1] for tgt in self._targets]
            if obj_info not in targets_info and obj_location is not None:
                obj = instantiate_object(object_def, obj_location)
                object_list.append(obj)

    def parse_path_section(self, path_section, current_heading):
        index = 1
        actions = []
        dx = path_section[1][0]-path_section[0][0]
        dz = path_section[1][1]-path_section[0][1]
        theta = degrees(arctan2(dx,dz))
  
            #IF my calculations are correct, this should be right no matter what
            # I'm assuming a positive angle is a clockwise rotation- so this should work
            #I think

        delta_t = current_heading-theta
        current_heading = theta
        if delta_t != 0:
            action = {
                'action': 'RotateLook',
                'params': {
                    'rotation': round(delta_t,0),
                    'horizon': 0.0
                    }
                }
            actions.append(action)
        distance = sqrt( dx ** 2 + dz ** 2 )
        frac, whole = math.modf(distance / MAX_MOVE_DISTANCE)
        actions.extend([{
                    "action": "MoveAhead",
                    "params": {}
                    }]*int(whole))
        actions.append({
                "action": "MoveAhead",
                "params": {
                    "amount": round(frac,POSITION_DIGITS)
                    }
            })
        return actions

    @abstractmethod
    def get_config(self, goal_objects):
        """Get the goal configuration. goal_objects is the objects required for the goal (as returned from
        compute_objects)."""
        pass

    def generate_walls(self, material, performer_position, bounding_rects):
        wall_count = random.choices(WALL_COUNTS, weights=WALL_PROBS, k=1)[0]

        walls = []
        for x in range(0, wall_count):
            wall = generate_wall(material, performer_position, bounding_rects)
            if wall is not None:
                walls.append(wall)
            else:
                logging.warning('could not generate wall')
        return walls

    @abstractmethod
    def find_optimal_path(self, goal_objects, all_objects):
        """Compute the optimal set of moves and update the body object"""
        pass
       
    @staticmethod
    def find_all_valid_objects(constraint_list, objects):
        """Find all members of objects that satisfy all constraints in constraint_list"""
        valid_objects = []
        for obj in objects:
            obj_ok = True
            for constraint in constraint_list:
                if not constraint.is_true(obj):
                    obj_ok = False
                    break
            if obj_ok:
                valid_objects.append(obj)
        return valid_objects


class EmptyGoal(Goal):
    """An empty goal."""

    def __init__(self):
        super(EmptyGoal, self).__init__()

    def compute_objects(self):
        return [], [], []

    def get_config(self, goal_objects):
        return ''

    def find_optimal_path(self, goal_objects, all_objects):
        return ''


class InteractionGoal(Goal, ABC):
    TARGET_CONTAINED_CHANCE = 0.25
    """Chance that the target will be in a container"""
    OBJECT_CONTAINED_CHANCE = 0.5
    """Chance that, if the target is in a container, a non-target pickupable object in the scene will be, too."""

    def __init__(self):
        super(InteractionGoal, self).__init__()
        self._bounding_rects = []

    def _set_performer_start(self):
        self._performer_start = self.compute_performer_start()

    def _set_target_def(self):
        """Chooses a pickupable object since most interaction goals require that."""
        pickupable_defs = random.choice(OBJECTS_PICKUPABLE_LISTS)
        self._target_def = finalize_object_definition(random.choice(pickupable_defs))

    def _set_target_location(self):
        performer_position = self._performer_start['position']
        self._target_location = calc_obj_pos(performer_position, self._bounding_rects, self._target_def)
        if self._target_location is None:
            raise GoalException(f'could not place target object (type={self._target_def["type"]})')

    def _set_goal_objects(self):
        """Set all objects required for the goal other than the target, if any. May update _bounding_rects."""
        self._goal_objects = []

    def add_objects(self, all_objects, bounding_rects, performer_position):
        """Maybe add a container and put the target inside it. If so, maybe put other objects in other objects, too."""
        if random.random() <= self.TARGET_CONTAINED_CHANCE:
            if move_to_container(self._target, all_objects, bounding_rects, performer_position):
                # maybe do it with other objects, too
                super(InteractionGoal, self).add_objects(all_objects, bounding_rects, performer_position)
                for obj in all_objects:
                    if obj != self._target and obj.get('pickupable', False) \
                            and random.random() <= self.OBJECT_CONTAINED_CHANCE:
                        move_to_container(obj, all_objects, bounding_rects, performer_position)

    def compute_objects(self):
        self._set_performer_start()
        self._set_target_def()
        self._set_target_location()
        self._target = instantiate_object(self._target_def, self._target_location)
        self._set_goal_objects()
        
        all_objects = [self._target] + self._goal_objects
        all_goal_objects = all_objects.copy()
        self.add_objects(all_objects, self._bounding_rects, self._performer_start['position'])

        return all_goal_objects, all_objects, self._bounding_rects
        

class RetrievalGoal(InteractionGoal):
    """Going to a specified object and picking it up."""

    TEMPLATE = {
        'category': 'retrieval',
        'domain_list': ['objects', 'places', 'object_solidity', 'navigation', 'localization'],
        'type_list': ['interaction', 'action_full', 'retrieve'],
        'task_list': ['navigate', 'localize', 'retrieve'],
    }

    def __init__(self):
        super(RetrievalGoal, self).__init__()

    def get_config(self, objects):
        if len(objects) < 1:
            raise ValueError('need at least 1 object for this goal')

        target = objects[0]
        self._target = target
        self._targets.append(target)
        target_image_obj = find_image_for_object(target)
        image_name = find_image_name(target)

        goal = copy.deepcopy(self.TEMPLATE)
        goal['info_list'] = target['info']
        goal['metadata'] = {
            'target': {
                'id': target['id'],
                'info': target['info'],
                'match_image': True,
                'image': target_image_obj,
                'image_name': image_name
            }
        }
        goal['description'] = f'Find and pick up the {target["info"][-1]}.'
        return goal

    def find_optimal_path(self, goal_objects, all_objects):
        # Goal should be a singleton... I hope
        performer = (self._performer_start['position']['x'],self._performer_start['position']['z'])
        goal = (goal_objects[0]['shows'][0]['position']['x'],goal_objects[0]['shows'][0]['position']['z'])
        hole_rects=[]
        hole_rects.extend(object['shows'][0]['bounding_box'] for object in all_objects if object['id'] != goal_objects[0]['id'])
        path = generatepath(performer, goal, hole_rects)

        actions = []
        current_heading = self._performer_start['rotation']['y']
        for indx in range(len(path)-1):
            actions.extend(self.parse_path_section(path[indx:indx+2], current_heading))

        actions.append({
            'action': 'PickupObject',
            'params': {
                'objectId': goal_objects[0]['id']
                }
            })
        return actions
        

class TransferralGoal(InteractionGoal):
    """Moving a specified object to another specified object."""

    class RelationshipType(Enum):
        NEXT_TO = 'next to'
        ON_TOP_OF = 'on top of'

    TEMPLATE = {
        'category': 'transferral',
        'domain_list': ['objects', 'places', 'object_solidity', 'navigation', 'localization'],
        'type_list': ['interaction', 'identification', 'objects', 'places'],
        'task_list': ['navigation', 'identification', 'transportation']
    }

    def __init__(self):
        super(TransferralGoal, self).__init__()

    def _set_goal_objects(self):
        targets = objects.get_all_object_defs()
        random.shuffle(targets)
        target2_def = next((tgt for tgt in targets if 'stackTarget' in tgt.get('attributes', [])), None)
        if target2_def is None:
            raise ValueError(f'No stack targets found for transferral goal')
        target2_location = calc_obj_pos(self._performer_start['position'], self._bounding_rects, target2_def)
        target2 = instantiate_object(target2_def, target2_location)
        logging.debug(f'target2 = {target2}')
        self._goal_objects = [target2]

    def get_config(self, objects):
        if len(objects) < 2:
            raise ValueError(f'need at least 2 objects for this goal, was given {len(objects)}')
        target1, target2 = objects[0:2]
        if not target1.get('pickupable', False):
            raise ValueError(f'first object must be "pickupable": {target1}')
        if not target2.get('stackTarget', False):
            raise ValueError(f'second object must be "stackable": {target2}')
        relationship = random.choice(list(self.RelationshipType))

        self._targets.append([target1, target2])
        target1_image_obj = find_image_for_object(target1)
        target2_image_obj = find_image_for_object(target2)

        image_name1 = find_image_name(target1)
        image_name2 = find_image_name(target2)

        goal = copy.deepcopy(self.TEMPLATE)
        both_info = set(target1['info'] + target2['info'])
        goal['info_list'] = list(both_info)
        goal['metadata'] = {
            'target_1': {
                'id': target1['id'],
                'info': target1['info'],
                'match_image': True,
                'image': target1_image_obj,
                'image_name': image_name1
            },
            'target_2': {
                'id': target2['id'],
                'info': target2['info'],
                'match_image': True,
                'image': target2_image_obj,
                'image_name': image_name2
            },
            'relationship': ['target_1', relationship.value, 'target_2']
        }
        goal['description'] = f'Find and pick up the {target1["info"][-1]} and move it {relationship.value} ' \
            f'the {target2["info"][-1]}.'
        return goal

    def find_optimal_path(self, goal_objects, all_objects):
        # Goal should be a singleton... I hope
        performer = (self._performer_start['position']['x'],self._performer_start['position']['z'])
        goal = (goal_objects[0]['shows'][0]['position']['x'],goal_objects[0]['shows'][0]['position']['z'])
        hole_rects=[]
        hole_rects.extend(object['shows'][0]['bounding_box'] for object in all_objects if object['id'] != goal_objects[0]['id'])
        path = generatepath(performer, goal, hole_rects)
  
        actions = []
        current_heading = self._performer_start['rotation']['y']
        for indx in range(len(path)-1):
            actions.extend(self.parse_path_section(path[indx:indx+2], current_heading))

        actions.append({
            'action': 'PickupObject',
            'params': {
                'objectId': goal_objects[0]['id']
                }
            })
        target = (goal_objects[1]['shows'][0]['position']['x'], goal_objects[1]['shows'][0]['position']['z'])
        hole_rects = []
        hole_rects.extend(object['shows'][0]['bounding_box'] for object in all_objects if  ( object['id'] != goal_objects[0]['id'] and object['id'] != goal_objects[1]['id']))
        path  = generatepath(goal,target, hole_rects)
        for indx in range(len(path)-1):
            actions.extend(self.parse_path_section(path[indx:indx+2], current_heading))
            
        actions.append({
            'action': 'PutObject',
            'params': {
                'objectId': goal_objects[0]['id'] ,
                'receptacleObjectId': goal_objects[1]['id']
                }})
  
        return actions


class TraversalGoal(Goal):
    """Locating and navigating to a specified object."""

    TEMPLATE = {
        'category': 'traversal',
        'domain_list': ['objects', 'places', 'object_solidity', 'navigation', 'localization'],
        'type_list': ['interaction', 'action_full', 'traversal'],
        'task_list': ['navigate', 'localize', 'traversal'],
    }

    def __init__(self):
        super(TraversalGoal, self).__init__()

    def compute_objects(self):
        # add objects we need for the goal
        target_def = self.choose_object_def()
        performer_start = self.compute_performer_start()
        performer_position = performer_start['position']
        bounding_rects = []
        target_location = calc_obj_pos(performer_position, bounding_rects, target_def)
        if target_location is None:
            raise GoalException('could not place target object')

        target = instantiate_object(target_def, target_location)
        self._targets.append(target)
        all_objects = [target]
        self.add_objects(all_objects, bounding_rects, performer_position)

        return [target], all_objects, bounding_rects

    def get_config(self, objects):
        if len(objects) < 1:
            raise ValueError('need at least 1 object for this goal')

        target = objects[0]

        target_image_obj = find_image_for_object(target)
        image_name = find_image_name(target)

        goal = copy.deepcopy(self.TEMPLATE)
        goal['info_list'] = target['info']
        goal['metadata'] = {
            'target': {
                'id': target['id'],
                'info': target['info'],
                'match_image': True,
                'image': target_image_obj,
                'image_name': image_name
            }
        }
        goal['description'] = f'Find the {target["info"][-1]} and move near it.'
        return goal

    def find_optimal_path(self, goal_objects, all_objects):
        # Goal should be a singleton... I hope
        performer = (self._performer_start['position']['x'],self._performer_start['position']['z'])
        goal = (goal_objects[0]['shows'][0]['position']['x'],goal_objects[0]['shows'][0]['position']['z'])
        hole_rects = []
        hole_rects.extend(object['shows'][0]['bounding_box'] for object in all_objects if object['id'] != goal_objects[0]['id'])
        path = generatepath(performer, goal, hole_rects)

        actions = []
        current_heading = self._performer_start['rotation']['y']
        for indx in range(len(path)-1):
            actions.extend(self.parse_path_section(path[indx:indx+2], current_heading))

        return actions


class IntPhysGoal(Goal, ABC):
    """Base class for Intuitive Physics goals. Subclasses must set TEMPLATE variable (for use in get_config)."""

    # The 3.55 or 4.2 is the position at which the object will leave the camera's viewport, and is dependent on the
    # object's Z position (either 1.6 or 2.7). The * 1.2 is to account for the camera's perspective.
    VIEWPORT_LIMIT_NEAR = 3.55
    VIEWPORT_LIMIT_FAR = 4.2
    VIEWPORT_PERSPECTIVE_FACTOR = 1.2

    def __init__(self):
        super(IntPhysGoal, self).__init__()

    def compute_performer_start(self):
        if self._performer_start is None:
            self._performer_start = {
                'position': {
                    'x': 0,
                    'y': 0,
                    'z': -4.5
                },
                'rotation': {
                    'y': 0
                }
            }
        return self._performer_start

    def update_body(self, body, find_path):
        body = super(IntPhysGoal, self).update_body(body, find_path)
        body['observation'] = True
        body['answer'] = {
            'choice': 'plausible'
        }
        return body

    def find_optimal_path(self, goal_objects, all_objects):
        return ''

    def _get_last_step(self):
        return 40

    def get_config(self, goal_objects):
        goal = copy.deepcopy(self.TEMPLATE)
        goal['last_step'] = self._get_last_step()
        goal['action_list'] = [['Pass']] * goal['last_step']
        return goal

    def generate_walls(self, material, performer_position, bounding_rects):
        """IntPhys goals have no walls."""
        return []

    def compute_objects(self):
        func = random.choice([IntPhysGoal._get_objects_moving_across, IntPhysGoal._get_objects_falling_down])
        objs = func(self)
        return [], objs, []

    def _get_objects_moving_across(self):
        num_objects = random.choices((1, 2, 3), (40, 30, 30))[0]
        object_positions = {
            'a': (4.2, 1.6),
            'b': (5.3, 1.6),
            'c': (4.8, 2.7),
            'd': (5.9, 2.7),
            'e': (-4.2, 1.6),
            'f': (-5.3, 1.6),
            'g': (-4.8, 2.7),
            'h': (-5.9, 2.7)
        }
        exclusions = {
            'a': ('e', 'f'),
            'b': ('e', 'f'),
            'c': ('g', 'h'),
            'd': ('g', 'h'),
            'e': ('a', 'b'),
            'f': ('a', 'b'),
            'g': ('c', 'd'),
            'h': ('c', 'd')
        }
        # Object in key position must have velocities <= velocities
        # for object in value position (e.g., object in b must have
        # velocities <= velocities for object in a).
        velocity_ordering = {
            'b': 'a',
            'd': 'c',
            'f': 'e',
            'h': 'g'
        }
        available_locations = set(object_positions.keys())
        location_assignments = {}
        new_objects = []
        for i in range(num_objects):
            location = random.choice(list(available_locations))
            available_locations.remove(location)
            for loc in exclusions[location]:
                available_locations.discard(loc)
            # TODO: later this will get imported from objects (or somewhere else)
            from objects_intphys_v1 import OBJECTS_INTPHYS
            obj_def = finalize_object_definition(random.choice(OBJECTS_INTPHYS))
            remaining_intphys_options = obj_def['intphys_options'].copy()
            while len(remaining_intphys_options) > 0:
                intphys_option = random.choice(remaining_intphys_options)
                if location in velocity_ordering and velocity_ordering[location] in location_assignments:
                    # ensure the objects won't collide
                    other_obj = location_assignments[velocity_ordering[location]]
                    # TODO: compute value for collision (MCS-188)
                    collision = False
                    if not collision:
                        break
                    elif len(remaining_intphys_options) == 1:
                        # last chance, so just swap the items to make their relative velocities "ok"
                        location_assignments[location] = other_obj
                        location = velocity_ordering[location]
                        location_assignments[location] = None # to be assigned later
                        break
                else:
                    break
                remaining_intphys_options.remove(intphys_option)

            object_location = {
                'position': {
                    'x': object_positions[location][0],
                    'y': intphys_option['y'],
                    'z': object_positions[location][1]
                }
            }
            obj = instantiate_object(obj_def, object_location)
            location_assignments[location] = obj
            position_by_step = copy.deepcopy(intphys_option['position_by_step'])
            object_position_x = object_positions[location][0]
            # adjust position_by_step and remove outliers
            new_positions = []
            for position in position_by_step:
                if location in ('a', 'b', 'c', 'd'):
                    position = object_position_x - position
                else:
                    position = object_position_x + position
                new_positions.append(position)
            if location in ('a', 'b', 'e', 'f'):
                max_x = IntPhysGoal.VIEWPORT_LIMIT_NEAR + obj_def['scale']['x'] / 2.0 * IntPhysGoal.VIEWPORT_PERSPECTIVE_FACTOR
            else:
                max_x = IntPhysGoal.VIEWPORT_LIMIT_FAR + obj_def['scale']['x'] / 2.0 * IntPhysGoal.VIEWPORT_PERSPECTIVE_FACTOR
            filtered_position_by_step = [position for position in new_positions if (abs(position) <= max_x)]
            # set shows.stepBegin
            min_stepBegin = 13
            if location in velocity_ordering and velocity_ordering[location] in location_assignments:
                min_stepBegin = location_assignments[velocity_ordering[location]]['shows'][0]['stepBegin']
            stepsBegin = random.randint(min_stepBegin, 55 - len(filtered_position_by_step))
            obj['shows'][0]['stepsBegin'] = stepsBegin
            obj['forces'] = [{
                'stepBegin': stepsBegin,
                'stepEnd': 55,
                'vector': intphys_option['force']
            }]
            if location in ('a', 'b', 'c', 'd'):
                obj['forces'][0]['vector']['x'] *= -1
            intphys_option['position_by_step'] = filtered_position_by_step
            obj['intphys_options'] = intphys_option
            new_objects.append(obj)

        return new_objects

    def _get_objects_falling_down(self):
        # TODO: in a future ticket
        return []


class GravityGoal(IntPhysGoal):
    TEMPLATE = {
        'category': 'intphys',
        'domain_list': ['objects', 'object_solidity', 'object_motion', 'gravity'],
        'type_list': ['observation', 'action_none', 'intphys', 'gravity'],
        'task_list': ['choose'],
        'description': '',
        'metadata': {}
    }

    def __init__(self):
        super(GravityGoal, self).__init__()
        self.OBJECT_PROBABILITIES = (
            (IntPhysGoal._get_objects_falling_down, GravityGoal._get_ramp_going_down, GravityGoal._get_ramp_going_up),
            (20, 60, 20)
        )

    def compute_objects(self):
        func = random.choices(self.OBJECT_PROBABILITIES[0], self.OBJECT_PROBABILITIES[1])[0]
        objs = func(self)
        return [], objs, []

    def _get_ramp_going_down(self):
        # TODO: in a future ticket
        return []

    def _get_ramp_going_up(self):
        # TODO: in a future ticket
        return []


class ObjectPermanenceGoal(IntPhysGoal):
    TEMPLATE = {
        'category': 'intphys',
        'domain_list': ['objects', 'object_solidity', 'object_motion', 'object_permanence'],
        'type_list': ['observation', 'action_none', 'intphys', 'object_permanence'],
        'task_list': ['choose'],
        'description': '',
        'metadata': {}
    }

    def __init__(self):
        super(ObjectPermanenceGoal, self).__init__()


class ShapeConstancyGoal(IntPhysGoal):
    TEMPLATE = {
        'category': 'intphys',
        'domain_list': ['objects', 'object_solidity', 'object_motion', 'object_permanence'],
        'type_list': ['observation', 'action_none', 'intphys', 'shape_constancy'],
        'task_list': ['choose'],
        'description': '',
        'metadata': {}
    }

    def __init__(self):
        super(ShapeConstancyGoal, self).__init__()


class SpatioTemporalContinuityGoal(IntPhysGoal):
    TEMPLATE = {
        'category': 'intphys',
        'domain_list': ['objects', 'object_solidity', 'object_motion', 'object_permanence'],
        'type_list': ['observation', 'action_none', 'intphys', 'spatio_temporal_continuity'],
        'task_list': ['choose'],
        'description': '',
        'metadata': {}
    }

    def __init__(self):
        super(SpatioTemporalContinuityGoal, self).__init__()

    def _get_last_step(self):
        return 60


# Note: the names of all goal classes in GOAL_TYPES must end in "Goal" or choose_goal will not work
GOAL_TYPES = {
    'interaction': [RetrievalGoal, TransferralGoal, TraversalGoal],
# uncomment intphys goals when they have objects
#    'intphys': [GravityGoal, ObjectPermanenceGoal, ShapeConstancyGoal, SpatioTemporalContinuityGoal]
}


def choose_goal(goal_type):
    """Return a random class of 'goal' object from within the specified
overall type, or EmptyGoal if goal_type is None"""
    if goal_type is None:
        return EmptyGoal()
    else:
        if goal_type in GOAL_TYPES:
            return random.choice(GOAL_TYPES[goal_type])()
        else:
            class_name = goal_type + 'Goal'
            print(globals().keys())
            klass = globals()[class_name]
            return klass()


def get_goal_types():
    generic_types = GOAL_TYPES.keys()
    specific_types = [ klass.__name__.replace('Goal','') for classes in GOAL_TYPES.values() for klass in classes]
    return list(generic_types) + specific_types

