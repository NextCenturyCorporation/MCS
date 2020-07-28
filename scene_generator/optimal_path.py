import logging
import traceback
from typing import List, Dict, Tuple, Optional

from shapely.geometry import Polygon, Point
from shapely.ops import unary_union

from extremitypathfinder.extremitypathfinder import PolygonEnvironment as Environment
from geometry import ROOM_X_MIN, ROOM_X_MAX, ROOM_Z_MIN, ROOM_Z_MAX
from util import PERFORMER_WIDTH


def _dilate_polygons(rects: List[List[Dict[str, float]]], dilation: float,
                     source: Point, target: Point) \
        -> Optional[List[Polygon]]:
    """Grow passed rectangles by dilation amount and return the resulting
    polygons, or None if the source or target are in any of the new,
    dilated polygons.
    """
    polygons = []
    for rect in rects:
        poly = Polygon([(point['x'], point['z']) for point in rect])
        poly.buffer(dilation, resolution=4)
        if poly.contains(source):
            logging.debug(f'source is inside something: source={source}\tpoly={poly}')
            return None
        if poly.contains(target):
            logging.debug(f'target is inside something: target={target}\tpoly={poly}')
            return None
        polygons.append(poly)
    return polygons


def _unify_and_clean_polygons(polygons: List[Polygon]) \
        -> List[List[Tuple[float, float]]]:
    """Unify any intersecting polygons and clean them up to be suitable
    for the path finding algorithm.
    """
    unified_polygons = unary_union(polygons)
    # unary_union can return Polygon or MultiPolygon
    if isinstance(unified_polygons, Polygon):
        unified_polygons = [unified_polygons]
    poly_coords = [list(poly.exterior.coords) for poly in unified_polygons]
    # The polygons we get back from unary_union can have the same
    # first and last point, which the shortest path algorithm doesn't
    # like.
    num_unified_points = 0
    for coords in poly_coords:
        num_unified_points += len(coords)
        if coords[0] == coords[-1]:
            del coords[-1]
    logging.debug(f'unified polygons: {len(poly_coords)}\tunified points: {num_unified_points}')

    return poly_coords


# passing the other_rects from my  calculations previously
# This is the source for extremitypathfinder: https://github.com/MrMinimal64/extremitypathfinder
# target_loc will probably contain the target- we'll see
def generatepath(source_loc: Tuple[float, float],
                 target_loc: Tuple[float, float],
                 other_rects: List[List[Dict[str, float]]],
                 agent_width: float = PERFORMER_WIDTH) \
        -> Optional[List[Tuple[float, float]]]:
    """Boundary has to be CCW, Holes CW"""
    # dilate all the polygons based on the agent width
    dilation = agent_width / 2.0
    polygons = _dilate_polygons(other_rects, dilation, Point(*source_loc), Point(*target_loc))
    if polygons is None:
        return None

    # they may intersect now, so unify any that do
    poly_coords = _unify_and_clean_polygons(polygons)

    environment = Environment()
    boundary_coordinates = [(ROOM_X_MAX - dilation, ROOM_Z_MAX - dilation),
                            (ROOM_X_MIN + dilation, ROOM_Z_MAX - dilation),
                            (ROOM_X_MIN + dilation, ROOM_Z_MIN + dilation),
                            (ROOM_X_MAX - dilation, ROOM_Z_MIN + dilation)]
    try:
        environment.store(boundary_coordinates, poly_coords, validate=True)
        environment.prepare()
        path, length = environment.find_shortest_path(source_loc, target_loc)
        # Work around a bug in the DirectedHeuristicGraph class
        # defined by the extremitypathfinder module. It causes the
        # graph to keep growing across successive Environments. See
        # https://github.com/MrMinimal64/extremitypathfinder/issues/10
        environment.graph.all_nodes.clear()
    except TypeError as e:
        # We sometimes get "TypeError: unsupported operand type(s) for
        # +: 'NoneType' and 'float'" and "'<' not supported between
        # instances of 'generator' and 'generator'", but I don't know
        # why.
        logging.info(f'path finding failed (maybe impossible?): {e}')
        return None
    except Exception:
        # We shouldn't get other exceptions from the path finder, but
        # just in case...
        logging.warning('unexpected error in path finding')
        traceback.print_exc()
        logObject = {
            'boundary': boundary_coordinates,
            'holes': poly_coords,
            'start': source_loc,
            'target': target_loc
        }
        logging.warning(logObject)
        return None
    return path
