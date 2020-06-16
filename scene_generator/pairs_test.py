from typing import Dict, Any

import geometry
from pairs import SimilarAdjacentPair

MAX_ADJACENT_DISTANCE = 0.5


def are_adjacent(obj_a: Dict[str, Any], obj_b: Dict[str, Any]) -> bool:
    poly_a = geometry.get_bounding_polygon(obj_a)
    poly_b = geometry.get_bounding_polygon(obj_b)
    distance = poly_a.distance(poly_b)
    return distance <= MAX_ADJACENT_DISTANCE


def test_SimilarAdjacentPair():
    pair = SimilarAdjacentPair({}, False)
    assert pair is not None


def test_SimilarAdjacentPair_get_scenes():
    pair = SimilarAdjacentPair({}, False)
    scene1, scene2 = pair.get_scenes()
    assert scene1 is not None
    assert scene2 is not None
    assert len(scene1['objects']) >= 1
    assert len(scene2['objects']) >= 2
    target1 = scene1['objects'][0]
    in_container = 'locationParent' in target1
    target2, similar = scene2['objects'][0:2]
    assert ('locationParent' in target2) == in_container
    assert ('locationParent' in similar) == in_container
    assert are_adjacent(target2, similar)
