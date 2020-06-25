import shapely

import geometry
from pairs import ImmediatelyVisiblePair, HiddenBehindPair, OneEnclosedPair


def test_ImmediatelyVisiblePair():
    pair = ImmediatelyVisiblePair({}, False)
    assert pair is not None


def test_ImmediatelyVisiblePair_get_scenes():
    pair = ImmediatelyVisiblePair({}, False)
    scene1, scene2 = pair.get_scenes()
    assert scene1 is not None
    assert scene2 is not None


def test_HiddenBehindPair_get_scenes():
    pair = HiddenBehindPair({}, False)
    scene1, scene2 = pair.get_scenes()
    assert scene1 is not None
    assert scene2 is not None
    # ensure the occluder is between the target and the performer
    target, occluder = scene2['objects'][0:2]
    assert target['dimensions']['x'] <= occluder['dimensions']['x']
    assert target['dimensions']['y'] <= occluder['dimensions']['y']
    target_position = target['shows'][0]['position']
    target_coords = (target_position['x'], target_position['z'])
    performer_position = scene2['performerStart']['position']
    performer_coords = (performer_position['x'], performer_position['z'])
    line_to_target = shapely.geometry.LineString([performer_coords, target_coords])

    occluder_poly = geometry.get_bounding_polygon(occluder)
    assert occluder_poly.intersects(line_to_target)


def test_OneEnclosedPair_get_scenes():
    pair = OneEnclosedPair({}, False)
    scene1, scene2 = pair.get_scenes()
    assert scene1 is not None
    assert scene2 is not None
    target, similar = scene1['objects'][0:2]
    assert ('locationParent' in target) != ('locationParent' in similar)
    target2, similar2 = scene2['objects'][0:2]
    assert ('locationParent' in target2) != ('locationParent' in similar2)
    assert ('locationParent' in target) == ('locationParent' in target2)
