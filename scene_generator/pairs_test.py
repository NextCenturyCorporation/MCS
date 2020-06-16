from geometry_test import are_adjacent
from pairs import SimilarAdjacentPair, SimilarFarPair


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


def test_SimilarFarPair():
    pair = SimilarFarPair({}, False)
    assert pair is not None


def test_SimilarFarPair_get_scenes():
    pair = SimilarFarPair({}, False)
    scene1, scene2 = pair.get_scenes()
    assert scene1 is not None
    assert scene2 is not None
    target = scene1['objects'][0]
    in_container = 'locationParent' in target
    target2, similar = scene2['objects'][0:2]
    assert target2 == target
    assert ('locationParent' in similar) == in_container
    if in_container:
        container1, container2 = scene2['objects'][2:4]
        assert not are_adjacent(container1, container2)
    else:
        assert not are_adjacent(target2, similar)

