#
# Goal generation
#

import copy
import logging
import random
import uuid
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Tuple, List, Dict, Any, Iterable

import geometry
import materials
import objects
import objects_intphys_v1
import ramps
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
MIN_RANDOM_INTERVAL = 0.05


def random_real(a, b, step=MIN_RANDOM_INTERVAL):
    """Return a random real number N where a <= N <= b and N - a is divisible by step."""
    steps = int((b - a) / step)
    n = random.randint(0, steps)
    return a + (n * step)


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
        goal_objects, all_objects, bounding_rects = self.compute_objects(body['wallMaterial'])
        walls = self.generate_walls(body['wallMaterial'], body['performerStart']['position'],
                                    bounding_rects)
        body['objects'] = all_objects + walls
        body['goal'] = self.get_config(goal_objects)
        if find_path:
            body['answer']['actions'] = self.find_optimal_path(goal_objects, all_objects+walls)

        info_set = set(body['goal'].get('info_list', []))
        for obj in body['objects']:
            info_set |= frozenset(obj.get('info', []))
        body['goal']['info_list'] = list(info_set)
        
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
    def compute_objects(self, wall_material_name):
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


class EmptyGoal(Goal):
    """An empty goal."""

    def __init__(self):
        super(EmptyGoal, self).__init__()

    def compute_objects(self, wall_material_name):
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

    def compute_objects(self, wall_material_name):
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

    def compute_objects(self, wall_material_name):
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

    MAX_OCCLUDER_TRIES = 100
    # The 3.55 or 4.2 is the position at which the object will leave the camera's viewport, and is dependent on the
    # object's Z position (either 1.6 or 2.7). The * 1.2 is to account for the camera's perspective.
    VIEWPORT_LIMIT_NEAR = 3.55
    VIEWPORT_LIMIT_FAR = 4.2
    VIEWPORT_PERSPECTIVE_FACTOR = 1.2
    OBJECT_NEAR_Z = 1.6
    OBJECT_FAR_Z = 2.7
    MIN_OCCLUDER_SCALE = 0.25
    MAX_OCCLUDER_SCALE = 1.0
    NEAR_X_PERSPECTIVE_FACTOR = 0.9
    FAR_X_PERSPECTIVE_FACTOR = 0.8
    # In each IntPhys scene containing occluders, the first 12 steps
    # involve moving and rotating the occluders, so the action should
    # start on step 13 at the earliest. The
    # objects-moving-across-behind-occluders scenes have 60 steps, and
    # the objects-falling-down-behind-occluders scenes have 40. The
    # last 6 steps of the scene involve moving and rotating the
    # occluders again. For objects-falling-down-behind-occluders
    # scenes, we reserve 8 steps for falling, and 8 steps for
    # post-falling actions, meaning that the objects can appear and
    # begin falling anytime between steps 13 and 20, inclusive.
    EARLIEST_ACTION_START_STEP = 13
    LATEST_ACTION_START_STEP = 20

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
        scenery_type = f'scenery_objects_{self._scenery_count}'
        goal['type_list'].append(scenery_type)

        return goal

    def generate_walls(self, material, performer_position, bounding_rects):
        """IntPhys goals have no walls."""
        return []

    def _compute_scenery(self):
        MIN_VISIBLE_X = -6.5
        MAX_VISIBLE_X = 6.5

        def random_x():
            return random_real(MIN_VISIBLE_X, MAX_VISIBLE_X, MIN_RANDOM_INTERVAL)

        def random_z():
            # Choose values so the scenery is placed between the
            # moving IntPhys objects and the room's wall.
            return random_real(3.25, 4.95, MIN_RANDOM_INTERVAL)

        self._scenery_count = random.choices((0, 1, 2, 3, 4, 5),
                                             (50, 10, 10, 10, 10, 10))[0]
        scenery_list = []
        scenery_rects = []
        scenery_defs = objects.OBJECTS_MOVEABLE + objects.OBJECTS_IMMOBILE
        for i in range(self._scenery_count):
            location = None
            while location is None:
                scenery_def = finalize_object_definition(random.choice(scenery_defs))
                location = calc_obj_pos(geometry.ORIGIN, scenery_rects, scenery_def,
                                        random_x, random_z)
            scenery_obj = instantiate_object(scenery_def, location)
            scenery_list.append(scenery_obj)
        return scenery_list

    def compute_objects(self, wall_material_name):
        func = random.choice([IntPhysGoal._get_objects_and_occluders_moving_across, IntPhysGoal._get_objects_falling_down])
        objs, occluders = func(self, wall_material_name)
        return [], objs + occluders, []

    def _get_num_occluders(self):
        """Return number of occluders for the scene."""
        return random.choices((1, 2, 3, 4), (40, 20, 20, 20))[0]

    def _get_num_paired_occluders(self):
        """Return how many occluders must be paired with a target object."""
        return 1
    
    def _get_occluders(self, obj_list, wall_material_name):
        """Get occluders to for objects in obj_list."""
        num_occluders = self._get_num_occluders()
        num_paired_occluders = self._get_num_paired_occluders()
        non_wall_materials = [m for m in materials.CEILING_AND_WALL_MATERIALS
                              if m[0] != wall_material_name]
        occluder_list = []
        # First add paired occluders. We want to position each paired
        # occluder at the same X position that its corresponding
        # object will be at the end/start of a random step during its
        # movement across the scene described by
        # position_by_step. This will let us add an implausible event
        # (make the object disappear, teleport it, or replace it with
        # another object) at that specific step.
        for i in range(num_paired_occluders):
            occluder_fits = False
            for _ in range(IntPhysGoal.MAX_OCCLUDER_TRIES):
                paired_obj = obj_list[i]
                min_scale = min(max(paired_obj['shows'][0]['scale']['x'], IntPhysGoal.MIN_OCCLUDER_SCALE), IntPhysGoal.MAX_OCCLUDER_SCALE)
                position_by_step = paired_obj['intphys_options']['position_by_step']
                position_index = random.randrange(len(position_by_step))
                paired_x = position_by_step[position_index]
                paired_z = paired_obj['shows'][0]['position']['z']
                if paired_z == IntPhysGoal.OBJECT_NEAR_Z:
                    occluder_x = paired_x * IntPhysGoal.NEAR_X_PERSPECTIVE_FACTOR
                elif paired_z == IntPhysGoal.OBJECT_FAR_Z:
                    occluder_x = paired_x * IntPhysGoal.FAR_X_PERSPECTIVE_FACTOR
                else:
                    logging.warning(f'Unsupported z for occluder target "{paired_obj["id"]}": {paired_z}')
                    occluder_x = paired_x
                x_scale = random_real(min_scale, IntPhysGoal.MAX_OCCLUDER_SCALE, MIN_RANDOM_INTERVAL)
                found_collision = False
                for other_occluder in occluder_list:
                    if geometry.occluders_too_close(other_occluder, occluder_x, x_scale):
                        found_collision = True
                        break
                if not found_collision:
                    occluder_fits = True
                    break
            if occluder_fits:
                occluder_objs = objects.create_occluder(random.choice(non_wall_materials),
                                                        random.choice(materials.METAL_MATERIALS),
                                                        occluder_x, x_scale)
                occluder_list.extend(occluder_objs)
                break
            else:
                logging.warning(f'could not fit required occluder at x={occluder_x}')
                raise GoalException(f'Could not add minimum number of occluders ({num_paired_occluders})')
        self._add_occluders(occluder_list, num_occluders - num_paired_occluders, non_wall_materials)
        return occluder_list

    def _add_occluders(self, occluder_list, num_to_add, non_wall_materials):
        """Create additional, non-paired occluders and add them to occluder_list."""
        for _ in range(num_to_add):
            occluder_fits = False
            for try_num in range(IntPhysGoal.MAX_OCCLUDER_TRIES):
                # try random position and scale until we find one that fits (or try too many times)
                min_scale = IntPhysGoal.MIN_OCCLUDER_SCALE
                x_scale = random_real(min_scale, IntPhysGoal.MAX_OCCLUDER_SCALE, MIN_RANDOM_INTERVAL)
                limit = 3.0 - x_scale / 2.0
                limit = int(limit / MIN_RANDOM_INTERVAL) * MIN_RANDOM_INTERVAL
                occluder_x = random_real(-limit, limit, MIN_RANDOM_INTERVAL)
                found_collision = False
                for other_occluder in occluder_list:
                    if geometry.occluders_too_close(other_occluder, occluder_x, x_scale):
                        found_collision = True
                        break
                if not found_collision:
                    occluder_fits = True
                    break
            if occluder_fits:
                occluder_objs = objects.create_occluder(random.choice(non_wall_materials),
                                                        random.choice(materials.METAL_MATERIALS),
                                                        occluder_x, x_scale)
                occluder_list.extend(occluder_objs)
            else:
                logging.debug(f'could not fit occluder at x={occluder_x}')

    class Position(Enum):
        RIGHT_FIRST_NEAR = auto()
        RIGHT_LAST_NEAR = auto()
        RIGHT_FIRST_FAR = auto()
        RIGHT_LAST_FAR = auto()
        LEFT_FIRST_NEAR = auto()
        LEFT_LAST_NEAR = auto()
        LEFT_FIRST_FAR = auto()
        LEFT_LAST_FAR = auto()

    def _get_objects_and_occluders_moving_across(self, wall_material_name: str):
        """Get objects to move across the scene and occluders for them. Returns (objects, occluders) pair."""
        new_objects = self._get_objects_moving_across(wall_material_name)
        occluders = self._get_occluders(new_objects, wall_material_name)
        return new_objects, occluders

    def _get_objects_moving_across(self, wall_material_name, valid_positions: Iterable = frozenset(Position),
                                   positions=None) -> List[Dict[str, Any]]:
        """Get objects to move across the scene. Returns objects."""
        num_objects = random.choices((1, 2, 3), (40, 30, 30))[0]
        # The following x positions start outside the camera viewport
        # and ensure that objects with scale 1 don't collide with each
        # other.
        object_positions = {
            IntPhysGoal.Position.RIGHT_FIRST_NEAR: (4.2, IntPhysGoal.OBJECT_NEAR_Z),
            IntPhysGoal.Position.RIGHT_LAST_NEAR: (5.3, IntPhysGoal.OBJECT_NEAR_Z),
            IntPhysGoal.Position.RIGHT_FIRST_FAR: (4.8, IntPhysGoal.OBJECT_FAR_Z),
            IntPhysGoal.Position.RIGHT_LAST_FAR: (5.9, IntPhysGoal.OBJECT_FAR_Z),
            IntPhysGoal.Position.LEFT_FIRST_NEAR: (-4.2, IntPhysGoal.OBJECT_NEAR_Z),
            IntPhysGoal.Position.LEFT_LAST_NEAR: (-5.3, IntPhysGoal.OBJECT_NEAR_Z),
            IntPhysGoal.Position.LEFT_FIRST_FAR: (-4.8, IntPhysGoal.OBJECT_FAR_Z),
            IntPhysGoal.Position.LEFT_LAST_FAR: (-5.9, IntPhysGoal.OBJECT_FAR_Z)
        }
        exclusions = {
            IntPhysGoal.Position.RIGHT_FIRST_NEAR: (IntPhysGoal.Position.LEFT_FIRST_NEAR, IntPhysGoal.Position.LEFT_LAST_NEAR),
            IntPhysGoal.Position.RIGHT_LAST_NEAR: (IntPhysGoal.Position.LEFT_FIRST_NEAR, IntPhysGoal.Position.LEFT_LAST_NEAR),
            IntPhysGoal.Position.RIGHT_FIRST_FAR: (IntPhysGoal.Position.LEFT_FIRST_FAR, IntPhysGoal.Position.LEFT_LAST_FAR),
            IntPhysGoal.Position.RIGHT_LAST_FAR: (IntPhysGoal.Position.LEFT_FIRST_FAR, IntPhysGoal.Position.LEFT_LAST_FAR),
            IntPhysGoal.Position.LEFT_FIRST_NEAR: (IntPhysGoal.Position.RIGHT_FIRST_NEAR, IntPhysGoal.Position.RIGHT_LAST_NEAR),
            IntPhysGoal.Position.LEFT_LAST_NEAR: (IntPhysGoal.Position.RIGHT_FIRST_NEAR, IntPhysGoal.Position.RIGHT_LAST_NEAR),
            IntPhysGoal.Position.LEFT_FIRST_FAR: (IntPhysGoal.Position.RIGHT_FIRST_FAR, IntPhysGoal.Position.RIGHT_LAST_FAR),
            IntPhysGoal.Position.LEFT_LAST_FAR: (IntPhysGoal.Position.RIGHT_FIRST_FAR, IntPhysGoal.Position.RIGHT_LAST_FAR)
        }
        # Object in key position must have acceleration <=
        # acceleration for object in value position (e.g., object in
        # RIGHT_LAST_NEAR must have acceleration <= acceleration for
        # object in RIGHT_FIRST_NEAR).
        acceleration_ordering = {
            Position.RIGHT_LAST_NEAR: Position.RIGHT_FIRST_NEAR,
            Position.RIGHT_LAST_FAR: Position.RIGHT_FIRST_FAR,
            Position.LEFT_LAST_NEAR: Position.LEFT_FIRST_NEAR,
            Position.LEFT_LAST_FAR: Position.LEFT_FIRST_FAR
        }
        available_locations = set(valid_positions)
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
                if location in acceleration_ordering and \
                   acceleration_ordering[location] in location_assignments:
                    # ensure the objects won't collide
                    acceleration = abs(intphys_option['force']['x'] / obj_def['mass'])
                    other_obj = location_assignments[acceleration_ordering[location]]
                    other_acceleration = abs(other_obj['intphys_option']['force']['x'] / other_obj['mass'])

                    collision = acceleration > other_acceleration
                    if not collision:
                        break
                    elif len(remaining_intphys_options) == 1:
                        # last chance, so just swap the items to make their relative acceleration "ok"
                        location_assignments[location] = other_obj
                        location = acceleration_ordering[location]
                        location_assignments[location] = None # to be assigned later
                        break
                else:
                    break
                remaining_intphys_options.remove(intphys_option)

            object_location = {
                'position': {
                    'x': object_positions[location][0],
                    'y': intphys_option['y'] + obj_def['position_y'],
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
                if location in (IntPhysGoal.Position.RIGHT_FIRST_NEAR, IntPhysGoal.Position.RIGHT_LAST_NEAR, IntPhysGoal.Position.RIGHT_FIRST_FAR, IntPhysGoal.Position.RIGHT_LAST_FAR):
                    position = object_position_x - position
                else:
                    position = object_position_x + position
                new_positions.append(position)
            if location in (IntPhysGoal.Position.RIGHT_FIRST_NEAR, IntPhysGoal.Position.RIGHT_LAST_NEAR, IntPhysGoal.Position.LEFT_FIRST_NEAR, IntPhysGoal.Position.LEFT_LAST_NEAR):
                max_x = IntPhysGoal.VIEWPORT_LIMIT_NEAR + obj_def['scale']['x'] / 2.0 * IntPhysGoal.VIEWPORT_PERSPECTIVE_FACTOR
            else:
                max_x = IntPhysGoal.VIEWPORT_LIMIT_FAR + obj_def['scale']['x'] / 2.0 * IntPhysGoal.VIEWPORT_PERSPECTIVE_FACTOR
            filtered_position_by_step = [position for position in new_positions if (abs(position) <= max_x)]
            # set shows.stepBegin
            min_stepBegin = IntPhysGoal.EARLIEST_ACTION_START_STEP
            if location in acceleration_ordering and acceleration_ordering[location] in location_assignments:
                min_stepBegin = location_assignments[acceleration_ordering[location]]['shows'][0]['stepBegin']
            stepsBegin = random.randint(min_stepBegin, 55 - len(filtered_position_by_step))
            obj['shows'][0]['stepsBegin'] = stepsBegin
            obj['forces'] = [{
                'stepBegin': stepsBegin,
                'stepEnd': 55,
                'vector': intphys_option['force']
            }]
            if location in (IntPhysGoal.Position.RIGHT_FIRST_NEAR, IntPhysGoal.Position.RIGHT_LAST_NEAR, IntPhysGoal.Position.RIGHT_FIRST_FAR, IntPhysGoal.Position.RIGHT_LAST_FAR):
                obj['forces'][0]['vector']['x'] *= -1
            intphys_option['position_by_step'] = filtered_position_by_step
            obj['intphys_option'] = intphys_option
            new_objects.append(obj)
            if positions is not None:
                positions.append(location)

        return new_objects

    def _get_objects_falling_down(self, wall_material_name):
        MAX_POSITION_TRIES = 100
        MIN_OCCLUDER_SEPARATION = 0.5
        # min scale for each occluder / 2, plus 0.5 separation
        # divided by the smaller scale factor for distance from viewpoint
        min_obj_distance = (IntPhysGoal.MIN_OCCLUDER_SCALE/2 + IntPhysGoal.MIN_OCCLUDER_SCALE/2 +
                            MIN_OCCLUDER_SEPARATION) / IntPhysGoal.FAR_X_PERSPECTIVE_FACTOR
        num_objects = random.choice((1, 2))
        object_list = []
        for i in range(num_objects):
            found_space = False
            # It doesn't matter how close the objects are to each
            # other, but each one must have an occluder, and those
            # have to be a certain distance apart, so these objects
            # do, too.
            for _ in range(MAX_POSITION_TRIES):
                # Choose x so the occluder (for this object) is fully
                # in the camera's viewport and with a gap so we can
                # see when an object enters/leaves the scene.
                x_position = random_real(-2.5, 2.5, MIN_RANDOM_INTERVAL)
                too_close = False
                for obj in object_list:
                    distance = abs(obj['shows'][0]['position']['x'] - x_position)
                    too_close = distance < min_obj_distance
                if not too_close:
                    found_space = True
            if not found_space:
                raise GoalException(f'Could not place {i+1} objects to fall down')
            location = {
                'position': {
                    'x': x_position,
                    'y': 3.8, # ensure the object starts above the camera viewport
                    'z': random.choice((IntPhysGoal.OBJECT_NEAR_Z, IntPhysGoal.OBJECT_FAR_Z))
                }
            }
            obj_def = random.choice(objects_intphys_v1.OBJECTS_INTPHYS)
            obj = instantiate_object(obj_def, location)
            obj['shows'][0]['stepBegin'] = random.randint(IntPhysGoal.EARLIEST_ACTION_START_STEP,
                                                          IntPhysGoal.LATEST_ACTION_START_STEP)
            object_list.append(obj)
        # place required occluders, then (maybe) some random ones
        num_occluders = 2 if num_objects == 2 else random.choice((1, 2))
        occluders = []
        non_wall_materials = [m for m in materials.CEILING_AND_WALL_MATERIALS
                              if m[0] != wall_material_name]
        for i in range(num_objects):
            paired_obj = object_list[i]
            min_scale = min(max(paired_obj['shows'][0]['scale']['x'], IntPhysGoal.MIN_OCCLUDER_SCALE), 1)
            x_position = paired_obj['shows'][0]['position']['x']
            paired_z = paired_obj['shows'][0]['position']['z']
            factor = IntPhysGoal.NEAR_X_PERSPECTIVE_FACTOR if paired_z == IntPhysGoal.OBJECT_NEAR_Z \
                else IntPhysGoal.FAR_X_PERSPECTIVE_FACTOR
            # Determine the biggest scale we could use for the new
            # occluder (up to 1) so it isn't too close to any of the
            # others.
            max_scale = IntPhysGoal.MAX_OCCLUDER_SCALE
            for occluder in occluders:
                distance = abs(occluder['shows'][0]['position']['x'] - x_position)
                scale = 2 * (distance - occluder['shows'][0]['scale']['x'] / 2.0 - MIN_OCCLUDER_SEPARATION)
                if scale < 0:
                    raise GoalException('Placed objects too close together after all')
                if scale < max_scale:
                    max_scale = scale
            x_scale = random_real(min_scale, max_scale, MIN_RANDOM_INTERVAL)
            adjusted_x = x_position * factor
            occluder_pair = objects.create_occluder(random.choice(non_wall_materials),
                                                    random.choice(materials.METAL_MATERIALS),
                                                    adjusted_x, x_scale, True)
            occluders.extend(occluder_pair)
        self._add_occluders(occluders, num_occluders - num_objects, non_wall_materials)

        return object_list, occluders


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

    def compute_objects(self, wall_material_name):
        objs = self._get_ramp_and_objects(wall_material_name)
        scenery = self._compute_scenery()
        return [], objs + scenery, []

    def _create_random_ramp(self) -> Tuple[ramps.Ramp, bool, List[Dict[str, Any]]]:
        material_name = random.choice(materials.OCCLUDER_MATERIALS)
        x_position_percent = random_real(0, 1)
        left_to_right = random.choice((True, False))
        ramp_type, ramp_objs = ramps.create_ramp(material_name, x_position_percent, left_to_right)
        return ramp_type, left_to_right, ramp_objs

    def _get_ramp_and_objects(self, wall_material_name):
        ramp_type, left_to_right, ramp_objs = self._create_random_ramp()
        if ramp_type in (ramps.Ramp.RAMP_90, ramps.Ramp.RAMP_30_90, ramps.Ramp.RAMP_45_90):
            # Don't put objects in places where they'd have to roll up
            # 90 degree (i.e., vertical) ramps.
            if left_to_right:
                valid_positions = { IntPhysGoal.Position.RIGHT_FIRST_NEAR, IntPhysGoal.Position.RIGHT_LAST_NEAR,
                                    IntPhysGoal.Position.RIGHT_FIRST_FAR, IntPhysGoal.Position.RIGHT_LAST_FAR }
            else:
                valid_positions = { IntPhysGoal.Position.LEFT_FIRST_NEAR, IntPhysGoal.Position.LEFT_LAST_NEAR,
                                    IntPhysGoal.Position.LEFT_FIRST_FAR, IntPhysGoal.Position.LEFT_LAST_FAR }
        else:
            valid_positions = set(IntPhysGoal.Position)
        positions = []
        objs = self._get_objects_moving_across(wall_material_name, valid_positions, positions)
        # adjust height to be on top of ramp if necessary
        for i in range(len(objs)):
            obj = objs[i]
            position = positions[i]
            if left_to_right and position in (
                    IntPhysGoal.Position.RIGHT_FIRST_NEAR, IntPhysGoal.Position.RIGHT_LAST_NEAR,
                    IntPhysGoal.Position.RIGHT_FIRST_FAR, IntPhysGoal.Position.RIGHT_LAST_FAR) or \
                    not left_to_right and position in (
                    IntPhysGoal.Position.LEFT_FIRST_NEAR, IntPhysGoal.Position.LEFT_LAST_NEAR,
                    IntPhysGoal.Position.LEFT_FIRST_FAR, IntPhysGoal.Position.LEFT_LAST_FAR):
                obj['shows'][0]['position']['y'] += ramps.RAMP_OBJECT_HEIGHTS[ramp_type]

        return ramp_objs + objs

    def _get_ramp_going_up(self, wall_material_name):
        # TODO: in a future ticket
        return [], []


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

    def _get_num_occluders(self):
        return random.choices((2, 3, 4), (40, 30, 30))[0]

    def _get_num_paired_occluders(self):
        return 2

    def _get_num_objects_moving_across(self):
        return random.choices((2, 3), (60, 40))[0]

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

