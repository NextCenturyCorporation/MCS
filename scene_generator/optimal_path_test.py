from shapely.geometry import Point, Polygon

from optimal_path import _dilate_polygons, _unify_and_clean_polygons


def test__dilate_polygons():
    rect = [
        {'x': -1.0, 'z': -1.0},
        {'x': -1.0, 'z': 1.0},
        {'x': 1.0, 'z': 1.0},
        {'x': 1.0, 'z': -1.0}
    ]
    outside = Point(5, 5)
    dilation = 0.5
    dilated = _dilate_polygons([rect], dilation, outside, outside)
    assert dilated is not None

    invalid = _dilate_polygons([rect], dilation, Point(0, 0), outside)
    assert invalid is None


def test__unify_and_clean_polygons():
    coords = [
        [(0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)],
        [(0.5, 0.0), (0.5, 1.0), (1.5, 1.0), (1.5, 0.0)]
    ]
    polygons = [Polygon(c) for c in coords]
    unified_coords = _unify_and_clean_polygons(polygons)
    assert len(unified_coords) == 1
