from typing import Dict, Any

from pairs import ImmediatelyVisiblePair, ImmediatelyVisibleSimilarPair


def test_ImmediatelyVisiblePair():
    pair = ImmediatelyVisiblePair({}, False)
    assert pair is not None


def test_ImmediatelyVisiblePair_get_scenes():
    pair = ImmediatelyVisiblePair({}, False)
    scene1, scene2 = pair.get_scenes()
    assert scene1 is not None
    assert scene2 is not None


def test_ImmediatelyVisibleSimilar():
    pair = ImmediatelyVisibleSimilarPair({}, False)
    assert pair is not None


def is_contained(obj: Dict[str, Any]) -> bool:
    return 'locationParent' in obj


def test_ImmediatelyVisibleSimilar_get_scenes():
    pair = ImmediatelyVisibleSimilarPair({}, False)
    scene1, scene2 = pair.get_scenes()
    assert scene1 is not None
    assert scene2 is not None
    target1, similar1 = scene1['objects'][0:2]
    assert is_contained(target1) == is_contained(similar1)
    target2, similar2 = scene2['objects'][0:2]
    assert is_contained(target2) == is_contained(similar2)
