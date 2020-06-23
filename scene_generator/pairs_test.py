from pairs import ImmediatelyVisiblePair


def test_ImmediatelyVisiblePair():
    pair = ImmediatelyVisiblePair({}, False)
    assert pair is not None

def test_ImmediatelyVisiblePair_get_scenes():
    pair = ImmediatelyVisiblePair({}, False)
    scene1, scene2 = pair.get_scenes()
    assert scene1 is not None
    assert scene2 is not None
