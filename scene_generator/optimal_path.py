import logging
import traceback

from shapely.geometry import Polygon, Point
from shapely.ops import unary_union

from extremitypathfinder.extremitypathfinder import PolygonEnvironment as Environment
from geometry import ROOM_DIMENSIONS, PERFORMER_WIDTH

MIN_X = ROOM_DIMENSIONS[0][0]
MAX_X = ROOM_DIMENSIONS[0][1]
MIN_Z = ROOM_DIMENSIONS[1][0]
MAX_Z = ROOM_DIMENSIONS[1][1]


# passing the other_rects from my  calculations previously
# This is the source for extremitypathfinder: https://github.com/MrMinimal64/extremitypathfinder
# target_loc will probably contain the target- we'll see
def generatepath(source_loc, target_loc, other_rects, agent_width=PERFORMER_WIDTH):
    """Boundary has to be CCW, Holes CW"""
    dilation = agent_width / 2.0
    boundary_coordinates = [(MAX_X - dilation, MAX_Z - dilation),
                            (MIN_X + dilation, MAX_Z - dilation),
                            (MIN_X + dilation, MIN_Z + dilation),
                            (MAX_X - dilation, MIN_Z + dilation)]
    holes = []
    # This way does make me a bit nervous- as this is coding
    # need to convert to lists of points
    for rect in other_rects:
        holes.append([(point['x'], point['z']) for point in rect])

    # dilate all the polygons based on the agent width
    source_point = Point(*source_loc)
    target_point = Point(*target_loc)
    num_boundary_points = 0
    polygons = []
    for hole in holes:
        # Warning: Increasing resolution can dramatically increase
        # time required for path finding.
        poly = Polygon(hole).buffer(dilation, resolution=4)
        if poly.contains(source_point):
            logging.debug(f'source is inside something: source={source_point}\tpoly={poly}')
            return None
        if poly.contains(target_point):
            logging.debug(f'target is inside something: target={target_point}\tpoly={poly}')
            return None
        polygons.append(poly)
        num_boundary_points += len(poly.exterior.coords)
    logging.debug(f'raw polygons: {len(polygons)}\traw points: {num_boundary_points}')

    # they may intersect now, so unify any that do
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

    environment = Environment()
    try:
        environment.store(boundary_coordinates, poly_coords, validate=True)
        environment.prepare()
        path, length = environment.find_shortest_path(source_loc, target_loc)
        # Work around a bug in the DirectedHeuristicGraph class
        # defined by the extremitypathfinder module. It causes the
        # graph to keep growing across successive Environments.
        environment.graph.all_nodes.clear()
    except TypeError as e:
        # We sometimes get "TypeError: unsupported operand type(s) for
        # +: 'NoneType' and 'float'" and "'<' not supported between
        # instances of 'generator' and 'generator'", but I don't know
        # why.
        logging.info(f'path finding failed (maybe impossible?): {e}')
        return None
    except Exception as e:
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
