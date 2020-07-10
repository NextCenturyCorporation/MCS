from typing import Dict, Any

import shapely

import containers
import geometry
from geometry_test import are_adjacent
from pairs import Number1Pair, Number2Pair, Number3Pair, Number4Pair, Number5Pair, Number6Pair, Number7Pair


BODY_TEMPLATE = {
    'wallMaterial': 'test_wall_material',
    'wallColors': ['test_wall_color'],
    'performerStart': {
        'position': {
            'x': 0,
            'y': 0,
            'z': 0
        },
        'rotation': {
            'x': 0,
            'y': 0,
            'z': 0
        }
    }
}


def test_SimilarAdjacentPair():
    pair = Number3Pair(BODY_TEMPLATE, False)
    assert pair is not None


def test_SimilarAdjacentPair_get_scenes():
    pair = Number3Pair(BODY_TEMPLATE, False)
    scene1, scene2 = pair.get_scenes()
    assert scene1 is not None
    assert scene2 is not None
    assert len(scene1['objects']) >= 1
    assert len(scene2['objects']) >= 2
    target1 = pair._goal_1.get_target_list()[0]
    in_container = 'locationParent' in target1
    target2 = pair._goal_2.get_target_list()[0]
    similar = pair._goal_2.get_distractor_list()[0]
    assert ('locationParent' in target2) == in_container
    assert ('locationParent' in similar) == in_container
    assert are_adjacent(target2, similar)


def test_SimilarFarPair():
    pair = Number4Pair(BODY_TEMPLATE, False)
    assert pair is not None


def test_SimilarFarPair_get_scenes():
    pair = Number4Pair(BODY_TEMPLATE, False)
    scene1, scene2 = pair.get_scenes()
    assert scene1 is not None
    assert scene2 is not None
    target = pair._goal_1.get_target_list()[0]
    in_container = 'locationParent' in target
    target2 = pair._goal_2.get_target_list()[0]
    similar = pair._goal_2.get_distractor_list()[0]
    assert target2 == target
    assert ('locationParent' in similar) == in_container
    if in_container:
        container1 = containers.get_parent(target2, scene2['objects'])
        container2 = containers.get_parent(similar, scene2['objects'])
        assert not are_adjacent(container1, container2)
    else:
        assert not are_adjacent(target2, similar)


def test_SimilarAdjacentFarPair():
    pair = Number5Pair(BODY_TEMPLATE, False)
    assert pair is not None


def test_SimilarAdjacentFarPair_get_scene():
    pair = Number5Pair(BODY_TEMPLATE, False)
    scene1, scene2 = pair.get_scenes()
    assert scene1 is not None
    assert scene2 is not None
    target = pair._goal_1.get_target_list()[0]
    similar = pair._goal_1.get_distractor_list()[0]
    is_contained = 'locationParent' in target
    assert is_contained == ('locationParent' in similar)
    if is_contained:
        assert target['locationParent'] == similar['locationParent']
    else:
        assert are_adjacent(target, similar)
    
    target2 = pair._goal_2.get_target_list()[0]
    similar2 = pair._goal_2.get_distractor_list()[0]
    if is_contained:
        assert target2['locationParent'] != similar2['locationParent']
        target2Parent = containers.get_parent(target2, scene2['objects'])
        similar2Parent = containers.get_parent(similar2, scene2['objects'])
        assert not are_adjacent(target2Parent, similar2Parent)
    else:
        assert not are_adjacent(target2, similar2)


def test_ImmediatelyVisiblePair():
    pair = Number1Pair(BODY_TEMPLATE, False)
    assert pair is not None


def test_ImmediatelyVisiblePair_get_scenes():
    pair = Number1Pair(BODY_TEMPLATE, False)
    scene1, scene2 = pair.get_scenes()
    assert scene1 is not None
    assert scene2 is not None


def test_ImmediatelyVisibleSimilar():
    pair = Number6Pair(BODY_TEMPLATE, False)
    assert pair is not None


def is_contained(obj: Dict[str, Any]) -> bool:
    return 'locationParent' in obj


def test_ImmediatelyVisibleSimilar_get_scenes():
    pair = Number6Pair(BODY_TEMPLATE, False)
    scene1, scene2 = pair.get_scenes()
    assert scene1 is not None
    assert scene2 is not None
    target1 = pair._goal_1.get_target_list()[0]
    similar1 = pair._goal_1.get_distractor_list()[0]
    assert is_contained(target1) == is_contained(similar1)
    target2 = pair._goal_2.get_target_list()[0]
    similar2 = pair._goal_2.get_distractor_list()[0]
    assert is_contained(target2) == is_contained(similar2)


def test_HiddenBehindPair_get_scenes():
    pair = Number2Pair(BODY_TEMPLATE, False)
    scene1, scene2 = pair.get_scenes()
    assert scene1 is not None
    assert scene2 is not None
    # ensure the obstructor is between the target and the performer
    target = pair._goal_2.get_target_list()[0]
    obstructor = pair._goal_2.get_distractor_list()[0]
    assert (target['dimensions']['x'] <= obstructor['dimensions']['x'] or \
            target['dimensions']['z'] <= obstructor['dimensions']['z'])
    assert target['dimensions']['y'] <= obstructor['dimensions']['y']
    target_position = target['shows'][0]['position']
    target_coords = (target_position['x'], target_position['z'])
    performer_position = scene2['performerStart']['position']
    performer_coords = (performer_position['x'], performer_position['z'])
    line_to_target = shapely.geometry.LineString([performer_coords, target_coords])
    obstructor_poly = geometry.get_bounding_polygon(obstructor)
    assert obstructor_poly.intersects(line_to_target)


def test_OneEnclosedPair_get_scenes():
    pair = Number7Pair(BODY_TEMPLATE, False)
    scene1, scene2 = pair.get_scenes()
    assert scene1 is not None
    assert scene2 is not None
    target = pair._goal_1.get_target_list()[0]
    similar = pair._goal_1.get_distractor_list()[0]
    assert ('locationParent' in target) != ('locationParent' in similar)
    target2 = pair._goal_2.get_target_list()[0]
    similar2 = pair._goal_2.get_distractor_list()[0]
    assert ('locationParent' in target2) != ('locationParent' in similar2)
    assert ('locationParent' in target) == ('locationParent' in target2)

