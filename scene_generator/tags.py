from typing import Any, Dict, List

# SHARED TAGS

INTERACTIVE = 'interactive'
PASSIVE = 'passive'

ACTION_NONE = 'action none'
ACTION_SOME = 'action some'
ACTION_FULL = 'action full'

# INTERACTIVE TAGS

TRAVERSAL = 'traversal'
RETRIEVAL = 'retrieval'
TRANSFERRAL = 'transferral'

# INTUITIVE_PHYSICS GOAL AND QUARTET TAGS

INTUITIVE_PHYSICS = 'intuitive physics'
FALL_DOWN = 'fall down'
MOVE_ACROSS = 'move across'

TELEPORT_DELAYED = 'teleport delayed'
TELEPORT_INSTANTANEOUS = 'teleport instantaneous'

GRAVITY = 'gravity'
GRAVITY_ACCELERATION_Q1 = 'gravity ramp up slower'
GRAVITY_ACCELERATION_Q2 = 'gravity ramp down faster'
GRAVITY_ACCELERATION_Q3 = 'gravity ramp up faster'
GRAVITY_ACCELERATION_Q4 = 'gravity ramp down slower'
GRAVITY_TRAJECTORY_Q1 = 'gravity ramp fast further'
GRAVITY_TRAJECTORY_Q2 = 'gravity ramp slow shorter'
GRAVITY_TRAJECTORY_Q3 = 'gravity ramp fast shorter'
GRAVITY_TRAJECTORY_Q4 = 'gravity ramp slow further'

OBJECT_PERMANENCE = 'object permanence'
OBJECT_PERMANENCE_Q1 = 'object permanence show object'
OBJECT_PERMANENCE_Q2 = 'object permanence show then hide object'
OBJECT_PERMANENCE_Q3 = 'object permanence hide then show object'
OBJECT_PERMANENCE_Q4 = 'object permanence hide object'

SHAPE_CONSTANCY = 'shape constancy'
SHAPE_CONSTANCY_Q1 = 'shape constancy object one'
SHAPE_CONSTANCY_Q2 = 'shape constancy object one into two'
SHAPE_CONSTANCY_Q3 = 'shape constancy object two into one'
SHAPE_CONSTANCY_Q4 = 'shape constancy object two'

SPATIO_TEMPORAL_CONTINUITY = 'spatio temporal continuity'
SPATIO_TEMPORAL_CONTINUITY_Q1 = 'spatio temporal continuity move earlier'  # noqa: E501
SPATIO_TEMPORAL_CONTINUITY_Q2 = 'spatio temporal continuity teleport forward'  # noqa: E501
SPATIO_TEMPORAL_CONTINUITY_Q3 = 'spatio temporal continuity teleport backward'  # noqa: E501
SPATIO_TEMPORAL_CONTINUITY_Q4 = 'spatio temporal continuity move later'

# MCS CORE DOMAIN TAGS

DOMAIN_OBJECTS = 'objects'
DOMAIN_OBJECTS_GRAVITY = 'gravity'
DOMAIN_OBJECTS_MOTION = 'object motion'
DOMAIN_OBJECTS_PERMANENCE = 'object permanence'
DOMAIN_OBJECTS_SOLIDITY = 'object solidity'

DOMAIN_PLACES = 'places'
DOMAIN_PLACES_LOCALIZATION = 'localization'
DOMAIN_PLACES_NAVIGATION = 'navigation'

# OBJECT TAGS

OBJECT_LOCATION_BACK = 'location in back of performer start'
OBJECT_LOCATION_CLOSE = 'location very close to target'
OBJECT_LOCATION_FAR = 'location far away from target'
OBJECT_LOCATION_FRONT = 'location in front of performer start'
OBJECT_LOCATION_RANDOM = 'location random'


def append_object_tags(
    tags: List[str], tag_to_objects: Dict[str, List[Dict[str, Any]]]
) -> List[str]:
    append_object_tags_of_type(tags, tag_to_objects['target'], 'target')
    if 'confusor' in tag_to_objects:
        append_object_tags_of_type(
            tags, tag_to_objects['confusor'], 'confusor')
    if 'distractor' in tag_to_objects:
        append_object_tags_of_type(
            tags, tag_to_objects['distractor'], 'distractor')
    if 'obstructor' in tag_to_objects:
        append_object_tags_of_type(
            tags, tag_to_objects['obstructor'], 'obstructor')
    for item in ['background object', 'confusor', 'distractor',
                 'obstructor', 'occluder', 'target', 'wall']:
        if item in tag_to_objects:
            number = len(tag_to_objects[item])
            if item == 'occluder':
                number = (int)(number / 2)
            tags.append(item + 's ' + str(number))
    return tags


def append_object_tags_of_type(
        tags: List[str], objs: List[Dict[str, Any]], name: str) -> List[str]:
    for obj in objs:
        enclosed_tag = (
            name +
            ' not enclosed') if obj.get(
            'locationParent',
            None) is None else (
            name +
            ' enclosed')
        novel_color_tag = (
            (name + ' novel color')
            if 'novelColor' in obj and obj['novelColor']
            else (name + ' not novel color')
        )
        novel_combination_tag = (
            (name + ' novel combination')
            if 'novelCombination' in obj and obj['novelCombination']
            else (name + ' not novel combination')
        )
        novel_shape_tag = (
            (name + ' novel shape')
            if 'novelShape' in obj and obj['novelShape']
            else (name + ' not novel shape')
        )
        for new_tag in [enclosed_tag, novel_color_tag,
                        novel_combination_tag, novel_shape_tag]:
            if new_tag not in tags:
                tags.append(new_tag)
    return tags


def get_containerize_tag(containerize: bool) -> str:
    return ('is' if containerize else 'isn\'t') + ' hidden inside receptacle'


def get_exists_tag(exists: bool) -> str:
    return ('does' if exists else 'doesn\'t') + ' exist'


def get_obstruct_vision_tag(obstruct_vision: bool) -> str:
    return ('does' if obstruct_vision else 'doesn\'t') + ' obstruct vision'


def get_ramp_tag(ramp_type_string: str) -> str:
    return 'ramp ' + ramp_type_string
