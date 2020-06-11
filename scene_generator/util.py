import copy
import logging
import uuid
import random
from typing import Dict, Any, Optional, List, Tuple

import materials


MAX_TRIES = 200
MIN_RANDOM_INTERVAL = 0.05


def random_real(a: float, b: float, step: float = MIN_RANDOM_INTERVAL) -> float:
    """Return a random real number N where a <= N <= b and N - a is divisible by step."""
    steps = int((b - a) / step)
    try:
        n = random.randint(0, steps)
    except ValueError as e:
        raise ValueError(f'bad args to random_real: ({a}, {b}, {step})', e)
    return a + (n * step)


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
