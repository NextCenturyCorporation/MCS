import copy
import logging
import uuid
import random
from typing import Dict, Any, Optional, List, Tuple, Iterable

import materials
import objects


def finalize_object_definition(object_def: Dict[str, Any]) -> Dict[str, Any]:
    object_def_copy = copy.deepcopy(object_def)

    # apply choice if necessary
    if 'choose' in object_def_copy:
        choice = random.choice(object_def_copy['choose'])
        for key in choice:
            object_def_copy[key] = choice[key]
        del object_def_copy['choose']

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
        'info': object_def['info'],
        'mass': object_def['mass']
    }
    if 'dimensions' in object_def:
        new_object['dimensions'] = object_def['dimensions']
    else:
        logging.warning(f'object type "{object_def["type"]}" has no dimensions')

    for attribute in object_def['attributes']:
        new_object[attribute] = True

    # need the original position for quartets
    new_object['original_location'] = copy.deepcopy(object_location)
    if 'offset' in object_def:
        object_location['position']['x'] -= object_def['offset']['x']
        object_location['position']['z'] -= object_def['offset']['z']

    if 'rotation' in object_def:
        object_location['rotation'] = copy.deepcopy(object_def['rotation'])

    shows = [object_location]
    new_object['shows'] = shows
    object_location['stepBegin'] = 0
    object_location['scale'] = object_def['scale']
    colors = set()
    if materials_list is None and 'materialCategory' in object_def:
        new_object['materialCategory'] = object_def['materialCategory']
        materials_list = [random.choice(getattr(materials, name.upper() + '_MATERIALS')) for name in
                          object_def['materialCategory']]
    if materials_list is not None:
        # need to remember materials for quartets
        new_object['materials_list'] = materials_list
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


def get_similar_definition(obj: Dict[str, Any]) -> Dict[str, Any]:
    choice = random.randint(1, 3)
    if choice == 1:
        return get_def_with_new_type(obj)
    elif choice == 2:
        return get_def_with_new_material(obj)
    else:
        return get_def_with_new_scale(obj)


def check_same_and_different(a: Dict[str, Any], b: Dict[str, Any],
                            same: Iterable[str], different: Iterable[str]) -> bool:
    """Return true iff for all properties in same that are in a, they
    exist in b and have the same value, and for all properties in
    different that are in a, they exist in b and are different.
    """
    same_ok = True
    for prop in same:
        if prop in a:
            if prop not in b or a[prop] != b[prop]:
                same_ok = False
                break
    if not same_ok:
        return False
    diff_ok = True
    for prop in different:
        if prop in a:
            if prop not in b or a[prop] == b[prop]:
                diff_ok = False
                break
    return diff_ok

    
def get_similar_defs(obj: Dict[str, Any], same: Iterable[str],
                     different: Iterable[str]) -> List[Dict[str, Any]]:
    """Return object definitions similar to obj: where properties from
    same are identical and from different are different. Raises a
    SceneException if none are found.
    """
    valid_defs = []
    for obj_def in objects.get_all_object_defs():
        if check_same_and_different(obj_def, obj, same, different):
            # now test the choose part if it's there
            if 'choose' in obj_def:
                valid_choices = [choice for choice in obj_def['choose']
                                 if check_same_and_different(choice, obj, same, different)]
                if len(valid_choices) != 0:
                    new_def = copy.deepcopy(obj_def)
                    new_def['choose'] = valid_choices
                    valid_defs.append(new_def)
            else:
                valid_defs.append(obj_def)
    if len(valid_defs) == 0:
        raise exceptions.SceneException(f'Cannot find anything similar to {obj} (same={same}, different={different})')
    return valid_defs


def get_def_with_new_type(obj: Dict[str, Any]) -> Dict[str, Any]:
    valid_defs = get_similar_defs(obj, ('materialCategory',
                                        'similarityScale'),
                                  ('type',))
    obj_def = random.choice(valid_defs)
    return obj_def


def get_def_with_new_material(obj: Dict[str, Any]) -> Dict[str, Any]:
    valid_defs = get_similar_defs(obj, ('type',
                                        'similarityScale'),
                                  ('materialCategory',))
    obj_def = random.choice(valid_defs)
    return obj_def


def get_def_with_new_scale(obj: Dict[str, Any]) -> Dict[str, Any]:
    valid_defs = get_similar_defs(obj, ('type',
                                        'materialCategory'),
                                  ('similarityScale',))
    obj_def = random.choice(valid_defs)
    return obj_def
