import copy
import logging
import random
import uuid
from typing import Dict, Any, Optional, List, Tuple, Iterable

import exceptions
import materials
import objects


MAX_SIZE_DIFFERENCE = 0.1
MAX_TRIES = 50
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


def finalize_object_definition(object_def: Dict[str, Any], choice_material: Optional[Dict[str, Any]] = None, \
        choice_size: Optional[Dict[str, Any]] = None, choice_type: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    object_def_copy = copy.deepcopy(object_def)

    if choice_material is None and 'chooseMaterial' in object_def_copy:
        choice_material = random.choice(object_def_copy['chooseMaterial'])

    if choice_size is None and 'chooseSize' in object_def_copy:
        choice_size = random.choice(object_def_copy['chooseSize'])

    if choice_type is None and 'chooseType' in object_def_copy:
        choice_type = random.choice(object_def_copy['chooseType'])

    if choice_material:
        for key in choice_material:
            object_def_copy[key] = choice_material[key]
        object_def_copy.pop('chooseMaterial', None)

    if choice_size:
        for key in choice_size:
            object_def_copy[key] = choice_size[key]
        object_def_copy.pop('chooseSize', None)

    if choice_type:
        for key in choice_type:
            object_def_copy[key] = choice_type[key]
        object_def_copy.pop('chooseType', None)

    return object_def_copy


def generate_materials_lists(material_category_list, previous_materials_lists):
    if len(material_category_list) == 0:
        return previous_materials_lists

    output_materials_lists = []
    material_category = material_category_list[0]
    for material_and_color in getattr(materials, material_category.upper() + '_MATERIALS'):
        if not previous_materials_lists:
            output_materials_lists.append([material_and_color])
        else:
            for material_list in previous_materials_lists:
                output_materials_lists.append(copy.deepcopy(material_list) + [material_and_color])
    return generate_materials_lists(material_category_list[1:], output_materials_lists)


def finalize_object_materials_and_colors(object_definition: Dict[str, Any], \
        override_materials_list: Optional[List[Tuple[str, List[str]]]] = None) -> List[Dict[str, Any]]:
    """Finalizes each possible choice of materials (patterns/textures) and colors as a copy of the given object
    definition and returns the list."""

    materials_lists = [override_materials_list] if override_materials_list else []

    if not 'materialCategory' in object_definition:
        object_definition['materialCategory'] = []

    if not materials_lists:
        materials_lists = generate_materials_lists(object_definition['materialCategory'], [])

    if not materials_lists:
        object_definition_copy = copy.deepcopy(object_definition)
        object_definition_copy['color'] = object_definition_copy['color'] if 'color' in object_definition_copy else []
        object_definition_copy['materials_list'] = []
        object_definition_copy['materials'] = object_definition_copy['materials'] if 'materials' in \
                object_definition_copy else []
        return [object_definition_copy]

    object_definition_list = []
    for materials_list in materials_lists:
        object_definition_copy = copy.deepcopy(object_definition)
        object_definition_copy['color'] = []
        object_definition_copy['materials_list'] = materials_list
        object_definition_copy['materials'] = [material_and_color[0] for material_and_color in materials_list]
        for material_and_color in materials_list:
            if material_and_color[0] in materials.NOVEL_COLOR_LIST:
                object_definition_copy['novelColor'] = True
            for color in material_and_color[1]:
                if color not in object_definition_copy['color']:
                    object_definition_copy['color'].append(color)
        object_definition_list.append(object_definition_copy)
    return object_definition_list



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

    if not 'mass' in object_def:
        print(f'mass missing {object_def}')

    new_object = {
        'id': str(uuid.uuid4()),
        'type': object_def['type'],
        'mass': object_def['mass'] * (object_def['massMultiplier'] if 'massMultiplier' in object_def else 1),
        'info': object_def['info'].copy(),
        'novelColor': object_def['novelColor'] if 'novelColor' in object_def else False,
        'novelCombination': object_def['novelCombination'] if 'novelCombination' in object_def else False,
        'novelShape': object_def['novelShape'] if 'novelShape' in object_def else False
    }
    if 'dimensions' in object_def:
        new_object['dimensions'] = object_def['dimensions']
    else:
        raise exceptions.SceneException(f'object definition "{object_def["type"]}" doesn\'t have dimensions')

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

    if 'color' not in object_def or 'materials' not in object_def:
        object_def = random.choice(finalize_object_materials_and_colors(object_def, materials_list))

    # need the materials list for quartets
    new_object['materials_list'] = object_def['materials_list']
    new_object['materials'] = object_def['materials']
    new_object['color'] = object_def['color']
    new_object['novelColor'] = (object_def['novelColor'] if 'novelColor' in object_def else False) or \
            new_object['novelColor']

    # The info list contains words that we can use to filter on specific object tags in the UI.
    # Start with this specific ordering of object tags in the info list needed for making the goal_string:
    # size weight color(s) material(s) shape
    if 'salientMaterials' in object_def:
        salient_materials = object_def['salientMaterials']
        new_object['salientMaterials'] = salient_materials
        new_object['info'] = new_object['info'][:1] + salient_materials + new_object['info'][1:]

    new_object['info'] = new_object['info'][:1] + list(new_object['color']) + new_object['info'][1:]

    if 'pickupable' in object_def['attributes']:
        weight = 'light'
    elif 'moveable' in object_def['attributes']:
        weight = 'heavy'
    else:
        weight = 'massive'
    new_object['info'] = new_object['info'][:1] + [weight] + new_object['info'][1:]

    # Use the object's goal_string for goal descriptions.
    new_object['goal_string'] = ' '.join(new_object['info'])

    # Save the object shape and size tags now before we add more tags to the end of the info list.
    new_object['shape'] = new_object['info'][-1]
    new_object['size'] = new_object['info'][0]

    if new_object['novelColor']:
        for color in list(new_object['color']):
            new_object['info'].append('novel ' + color)

    if new_object['novelShape']:
        new_object['info'].append('novel ' + new_object['shape'])

    # This object can't be marked as a novel combination if it's a novel color or a novel shape.
    if new_object['novelCombination'] and (new_object['novelColor'] or new_object['novelShape']):
        new_object['novelCombination'] = False

    if new_object['novelCombination']:
        for color in list(new_object['color']):
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
            new_obj = get_def_with_new_shape(obj, all_defs)
        elif choice == 2:
            new_obj = get_def_with_new_color(obj, all_defs)
        else:
            new_obj = get_def_with_new_size(obj, all_defs)
        if new_obj is not None:
            return new_obj
    return None


def check_same_and_different(a: Dict[str, Any], b: Dict[str, Any],
                             same: Iterable[str], different: Iterable[str]) -> bool:
    """Return true iff for all properties in same that are in a, they
    exist in b and have the same value, and for all properties in
    different that are in a, they exist in b and are different.
    """

    # TODO MCS-328 Remove
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
                    b[prop]['y'] > (a[prop]['y'] + MAX_SIZE_DIFFERENCE) or \
                    b[prop]['y'] < (a[prop]['y'] - MAX_SIZE_DIFFERENCE) or \
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
                    b[prop]['y'] <= (a[prop]['y'] + MAX_SIZE_DIFFERENCE) and \
                    b[prop]['y'] >= (a[prop]['y'] - MAX_SIZE_DIFFERENCE) and \
                    b[prop]['z'] <= (a[prop]['z'] + MAX_SIZE_DIFFERENCE) and \
                    b[prop]['z'] >= (a[prop]['z'] - MAX_SIZE_DIFFERENCE) and \
                    a['size'] == b['size']:
                diff_ok = False
                break
        elif (prop in a and prop in b and a[prop] == b[prop]) or \
                (not prop in a and not prop in b and a['type'] == b['type']):
            diff_ok = False
            break
    return diff_ok


def finalize_each_object_definition_choice(object_definition: Dict[str, Any]) -> List[Dict[str, Any]]:
    choice_list = []
    for prop in ['chooseMaterial', 'chooseSize', 'chooseType']:
        if prop in object_definition and len(object_definition[prop]) > 0:
            previous_choice_list = copy.deepcopy(choice_list)
            next_choice_list = []
            for choice_string in object_definition[prop]:
                if not previous_choice_list:
                    choice_dict = {'chooseMaterial': None, 'chooseSize': None, 'chooseType': None}
                    choice_dict[prop] = choice_string
                    next_choice_list.append(choice_dict)
                else:
                    for previous_choice_dict in previous_choice_list:
                        choice_dict = copy.deepcopy(previous_choice_dict)
                        choice_dict[prop] = choice_string
                        next_choice_list.append(choice_dict)
            choice_list = next_choice_list

    if not choice_list:
        return [finalize_object_definition(copy.deepcopy(object_definition))]

    output_list = []
    for choice_dict in choice_list:
        output_list.append(finalize_object_definition(copy.deepcopy(object_definition), \
                choice_material = choice_dict['chooseMaterial'], choice_size = choice_dict['chooseSize'], \
                choice_type = choice_dict['chooseType']))
    random.shuffle(output_list)
    return output_list


def get_similar_defs(obj: Dict[str, Any], all_defs: List[Dict[str, Any]], same: Iterable[str],
                     different: Iterable[str]) -> List[Dict[str, Any]]:
    """Return object definitions similar to obj: where properties from
    same are identical and from different are different.
    """

    valid_defs = []
    for obj_def in all_defs:
        possible_obj_defs = finalize_each_object_definition_choice(obj_def)
        for possible_obj_def_template in possible_obj_defs:
            possible_obj_def_list = finalize_object_materials_and_colors(possible_obj_def_template)
            for possible_obj_def in possible_obj_def_list:
                if check_same_and_different(possible_obj_def, obj, same, different):
                    valid_defs.append(possible_obj_def)
    return valid_defs


def get_def_with_new_shape(obj: Dict[str, Any], all_defs: List[Dict[str, Any]]) -> Dict[str, Any]:
    valid_defs = get_similar_defs(obj, all_defs, ('color', 'dimensions'), ('shape',))
    if len(valid_defs) == 0:
        return None
    obj_def = random.choice(valid_defs)
    # Save the similarity here for debugging
    obj_def['similarity'] = 'shape'
    return obj_def


def get_def_with_new_color(obj: Dict[str, Any], all_defs: List[Dict[str, Any]]) -> Dict[str, Any]:
    valid_defs = get_similar_defs(obj, all_defs, ('shape', 'dimensions'), ('color',))
    if len(valid_defs) == 0:
        return None
    obj_def = random.choice(valid_defs)
    # Save the similarity here for debugging
    obj_def['similarity'] = 'color'
    return obj_def


def get_def_with_new_size(obj: Dict[str, Any], all_defs: List[Dict[str, Any]]) -> Dict[str, Any]:
    valid_defs = get_similar_defs(obj, all_defs, ('shape', 'color'), ('dimensions',))
    if len(valid_defs) == 0:
        return None
    obj_def = random.choice(valid_defs)
    # Save the similarity here for debugging
    obj_def['similarity'] = 'size'
    return obj_def


def move_to_location(obj_def: Dict[str, Any], obj: Dict[str, Any], location: Dict[str, Any]) -> Dict[str, Any]:
    """Move the given object to a new location and return the object."""
    new_location = copy.deepcopy(location)
    if 'offset' in obj_def:
        new_location['position']['x'] -= obj_def['offset']['x']
        new_location['position']['z'] -= obj_def['offset']['z']
    obj['shows'][0]['position'] = new_location['position']
    obj['shows'][0]['rotation'] = new_location['rotation']
    if 'bounding_box' in new_location:
        obj['shows'][0]['bounding_box'] = new_location['bounding_box']
    return obj


def retrieve_full_object_definition_list(base_definition_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return the given object definition list in which finalize_object_definition was called on each definition with
    each possible choice."""
    object_definition_list = []
    for base_object_definition in base_definition_list:
        object_definition_list = object_definition_list + finalize_each_object_definition_choice(base_object_definition)
    return object_definition_list

