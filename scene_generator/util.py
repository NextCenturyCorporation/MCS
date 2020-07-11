import copy
import logging
import random
import uuid
from typing import Dict, Any, Optional, List, Tuple, Iterable

import exceptions
import materials
import objects


MAX_SIZE_DIFFERENCE = 0.1
MAX_TRIES = 100
MIN_RANDOM_INTERVAL = 0.05
PERFORMER_WIDTH = 0.1
PERFORMER_HALF_WIDTH = PERFORMER_WIDTH / 2.0


def random_real(a: float, b: float, step: float = MIN_RANDOM_INTERVAL) -> float:
    """Return a random real number N where a <= N <= b and N - a is divisible by step."""
    steps = int((b - a) / step)
    try:
        n = random.randint(0, steps)
    except ValueError as e:
        raise ValueError(f'bad args to random_real: ({a}, {b}, {step})', e)
    return a + (n * step)


def finalize_object_definition(object_def: Dict[str, Any],
                               choice: Optional[Dict[str, Any]] = None) \
                               -> Dict[str, Any]:
    object_def_copy = copy.deepcopy(object_def)

    # get choice if available and none provided
    if choice is None and 'choose' in object_def_copy:
        choice = random.choice(object_def_copy['choose'])

    if choice is not None:
        for key in choice:
            object_def_copy[key] = choice[key]
        object_def_copy.pop('choose', None)

    return object_def_copy


def instantiate_object(object_def: Dict[str, Any],
                       object_location: Dict[str, Any],
                       materials_list: Optional[List[Tuple[str, List[str]]]] = None) \
                       -> Dict[str, Any]:
    """Create a new object from an object definition (as from the objects.json file). object_location will be modified
    by this function."""
    if object_def is None or object_location is None:
        raise ValueError('instantiate_object cannot take None parameters')

    # Call the finalize function here in case it wasn't called before now (calling it twice shouldn't hurt anything).
    object_def = finalize_object_definition(object_def)

    new_object = {
        'id': str(uuid.uuid4()),
        'type': object_def['type'],
        'mass': object_def['mass'],
        'info': object_def['info'].copy(),
        'novel_color': object_def['novel_color'] if 'novel_color' in object_def else False,
        'novel_combination': object_def['novel_combination'] if 'novel_combination' in object_def else False,
        'novel_shape': object_def['novel_shape'] if 'novel_shape' in object_def else False
    }
    if 'dimensions' in object_def:
        new_object['dimensions'] = object_def['dimensions']
    else:
        exceptions.SceneException(f'object definition of type "{object_def["type"]}" doesn\'t have any dimensions')

    for attribute in object_def['attributes']:
        new_object[attribute] = True

    # need the original position for quartets
    new_object['original_location'] = copy.deepcopy(object_location)
    object_location = copy.deepcopy(object_location)
    if 'offset' in object_def:
        object_location['position']['x'] -= object_def['offset']['x']
        object_location['position']['z'] -= object_def['offset']['z']

    if not 'rotation' in object_def:
        object_def['rotation'] = {'x': 0, 'y': 0, 'z': 0}

    if not 'rotation' in object_location:
        object_location['rotation'] = {'x': 0, 'y': 0, 'z': 0}

    object_location['rotation']['x'] += object_def['rotation']['x']
    object_location['rotation']['y'] += object_def['rotation']['y']
    object_location['rotation']['z'] += object_def['rotation']['z']

    shows = [object_location]
    new_object['shows'] = shows
    object_location['stepBegin'] = 0
    object_location['scale'] = object_def['scale']
    colors = []
    if materials_list is None and 'materialCategory' in object_def:
        new_object['materialCategory'] = object_def['materialCategory']
        materials_list = [random.choice(getattr(materials, name.upper() + '_MATERIALS')) for name in
                          object_def['materialCategory']]
    if materials_list is not None:
        # need to remember materials for quartets
        new_object['materials_list'] = materials_list
        new_object['materials'] = [material_and_color[0] for material_and_color in materials_list]
        for material_and_color in materials_list:
            if material_and_color[0] in materials.NOVEL_COLOR_LIST:
                new_object['novel_color'] = True
            for color in material_and_color[1]:
                if color not in colors:
                    colors.append(color)

    # The info list contains words that we can use to filter on specific object tags in the UI.
    # Start with this specific ordering of object tags in the info list needed for making the goal_string:
    # size weight color(s) material(s) shape
    if 'salientMaterials' in object_def:
        salient_materials = object_def['salientMaterials']
        new_object['salientMaterials'] = salient_materials
        new_object['info'] = new_object['info'][:1] + salient_materials + new_object['info'][1:]

    new_object['info'] = new_object['info'][:1] + list(colors) + new_object['info'][1:]

    if 'pickupable' in object_def['attributes']:
        weight = 'light'
    elif 'moveable' in object_def['attributes']:
        weight = 'heavy'
    else:
        weight = 'massive'
    new_object['info'] = new_object['info'][:1] + [weight] + new_object['info'][1:]

    # Save a string of the joined info list that we can use to filter on the specific object in the UI.
    new_object['info_string'] = ' '.join(new_object['info'])

    # Use the object's goal_string for goal descriptions.
    new_object['goal_string'] = new_object['info_string']

    # Save the object shape and size tags now before we add more tags to the end of the info list.
    new_object['shape'] = new_object['info'][-1]
    new_object['size'] = new_object['info'][0]

    if new_object['novel_color']:
        for color in list(colors):
            new_object['info'].append('novel ' + color)

    if new_object['novel_shape']:
        new_object['info'].append('novel ' + new_object['shape'])

    # This object can't be marked as a novel combination if it's a novel color or a novel shape.
    if new_object['novel_combination'] and (new_object['novel_color'] or new_object['novel_shape']):
        new_object['novel_combination'] = False

    if new_object['novel_combination']:
        for color in list(colors):
            new_object['info'].append('novel ' + color + ' ' + new_object['shape'])

    return new_object


def get_similar_definition(obj: Dict[str, Any], all_defs: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Get an object definition similar to obj but different in one of
    type, material, or scale. It is possible but unlikely that no such
    definition can be found, in which case it returns None.
    """
    choices = [1, 2, 3]
    random.shuffle(choices)
    for choice in choices:
        if choice == 1:
            new_obj = get_def_with_new_type(obj, all_defs)
        elif choice == 2:
            new_obj = get_def_with_new_material(obj, all_defs)
        else:
            new_obj = get_def_with_new_scale(obj, all_defs)
        if new_obj is not None:
            return new_obj
    return None


def check_same_and_different(a: Dict[str, Any], b: Dict[str, Any],
                             same: Iterable[str], different: Iterable[str]) -> bool:
    """Return true iff for all properties in same that are in a, they
    exist in b and have the same value, and for all properties in
    different that are in a, they exist in b and are different.
    """

    a['shape'] = a['shape'] if 'shape' in a else a['info'][-1]
    a['size'] = a['size'] if 'size' in a else a['info'][0]
    b['shape'] = b['shape'] if 'shape' in b else b['info'][-1]
    b['size'] = b['size'] if 'size' in b else b['info'][0]

    same_ok = True
    for prop in same:
        if prop == 'dimensions':
            # Look at the dimensions as well as the size tag (tiny/small/medium/large/huge/etc.)
            if b[prop]['x'] > (a[prop]['x'] + MAX_SIZE_DIFFERENCE) or \
                    b[prop]['x'] < (a[prop]['x'] - MAX_SIZE_DIFFERENCE) or \
                    b[prop]['z'] > (a[prop]['z'] + MAX_SIZE_DIFFERENCE) or \
                    b[prop]['z'] < (a[prop]['z'] - MAX_SIZE_DIFFERENCE) or \
                    a['size'] != b['size']:
                same_ok = False
                break
        elif (prop in a and prop not in b) or (prop not in a and prop in b) or \
                (prop in a and prop in b and a[prop] != b[prop]):
            same_ok = False
            break
    if not same_ok:
        return False

    diff_ok = True
    for prop in different:
        if prop == 'dimensions':
            # Look at the dimensions as well as the size tag (tiny/small/medium/large/huge/etc.)
            if b[prop]['x'] <= (a[prop]['x'] + MAX_SIZE_DIFFERENCE) and \
                    b[prop]['x'] >= (a[prop]['x'] - MAX_SIZE_DIFFERENCE) and \
                    b[prop]['z'] <= (a[prop]['z'] + MAX_SIZE_DIFFERENCE) and \
                    b[prop]['z'] >= (a[prop]['z'] - MAX_SIZE_DIFFERENCE) and \
                    a['size'] == b['size']:
                diff_ok = False
                break
        elif (prop in a and prop in b and a[prop] == b[prop]) or (not prop in a and not prop in b):
            diff_ok = False
            break
    return diff_ok

    
def get_similar_defs(obj: Dict[str, Any], all_defs: List[Dict[str, Any]], same: Iterable[str],
                     different: Iterable[str]) -> List[Dict[str, Any]]:
    """Return object definitions similar to obj: where properties from
    same are identical and from different are different.
    """
    valid_defs = []
    for obj_def in all_defs:
        if 'choose' in obj_def:
            valid_choices = []
            for choice in obj_def['choose']:
                possible_obj_def = finalize_object_definition(copy.deepcopy(obj_def), choice)
                if check_same_and_different(possible_obj_def, obj, same, different):
                    valid_choices.append(choice)
            if len(valid_choices) > 0:
                new_def = copy.deepcopy(obj_def)
                new_def['choose'] = valid_choices
                valid_defs.append(new_def)
        else:
            possible_obj_def = finalize_object_definition(copy.deepcopy(obj_def))
            if check_same_and_different(possible_obj_def, obj, same, different):
                valid_defs.append(obj_def)
    return valid_defs


def get_def_with_new_type(obj: Dict[str, Any], all_defs: List[Dict[str, Any]]) -> Dict[str, Any]:
    valid_defs = get_similar_defs(obj, all_defs, ('materialCategory', 'dimensions'), ('shape',))
    if len(valid_defs) > 0:
        obj_def = random.choice(valid_defs)
    else:
        obj_def = None
    return obj_def


def get_def_with_new_material(obj: Dict[str, Any], all_defs: List[Dict[str, Any]]) -> Dict[str, Any]:
    valid_defs = get_similar_defs(obj, all_defs, ('shape', 'dimensions'), ('materialCategory',))
    if len(valid_defs) > 0:
        obj_def = random.choice(valid_defs)
    else:
        obj_def = None
    return obj_def


def get_def_with_new_scale(obj: Dict[str, Any], all_defs: List[Dict[str, Any]]) -> Dict[str, Any]:
    valid_defs = get_similar_defs(obj, all_defs, ('shape', 'materialCategory'), ('dimensions',))
    if len(valid_defs) > 0:
        obj_def = random.choice(valid_defs)
    else:
        obj_def = None
    return obj_def

