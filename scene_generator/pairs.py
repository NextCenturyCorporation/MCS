import copy
import logging
import random
from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any, Type, Optional

import shapely

import containers
import exceptions
import geometry
import objects
import util
from geometry import ROOM_DIMENSIONS, MIN_START_DISTANCE_AWAY


MAX_EXTRA_OBJECTS = 10
PERFORMER_BOUNDS = ((ROOM_DIMENSIONS[0][0] + MIN_START_DISTANCE_AWAY,
                     ROOM_DIMENSIONS[0][1] - MIN_START_DISTANCE_AWAY),
                    (ROOM_DIMENSIONS[1][0] + MIN_START_DISTANCE_AWAY,
                     ROOM_DIMENSIONS[1][1] - MIN_START_DISTANCE_AWAY))
"""(minX, maxX), (minZ, maxZ) for the performer (leaving space to put
an object in front of it)"""


def move_to_location(obj_def: Dict[str, Any], obj: Dict[str, Any],
                     location: Dict[str, Any]):
    """Move the passed object to a new location"""
    obj['original_location'] = copy.deepcopy(location)
    new_location = copy.deepcopy(location)
    if 'offset' in obj_def:
        new_location['position']['x'] -= obj_def['offset']['x']
        new_location['position']['z'] -= obj_def['offset']['z']
    obj['shows'][0]['position'] = new_location['position']
    obj['shows'][0]['rotation'] = new_location['rotation']
    if 'bounding_box' in new_location:
        obj['shows'][0]['bounding_box'] = new_location['bounding_box']


def instantiate_away_from(obj_def: Dict[str, Any],
                          performer_position: Dict[str, float],
                          old_obj: Dict[str, Any]) \
                          -> Optional[Dict[str, Any]]:
    """Instantiate obj_def in a location so that old_obj and the returned
    object are not adjacent. Returns None if it cannot find any such
    location for the new object.
    """
    for _ in range(util.MAX_TRIES):
        location = geometry.calc_obj_pos(performer_position, [], obj_def)
        new_obj = util.instantiate_object(obj_def, location)
        if not geometry.are_adjacent(old_obj, new_obj):
            return new_obj
    return None


def add_objects(target: Dict[str, Any], performer_position: Dict[str, float], scene: Dict[str, Any]):
    """Add 0 to MAX_EXTRA_OBJECTS to the scene with none between the
    performer and the target.
    """
    all_obj_defs = objects.get_all_object_defs()
    target_x = target['shows'][0]['position']['x']
    target_z = target['shows'][0]['position']['z']
    target_coords = geometry.calc_obj_coords(target_x, target_z,
                                             target['dimensions']['x'] / 2.0,
                                             target['dimensions']['z'] / 2.0,
                                             0, 0, target['shows'][0]['rotation']['y'])
    # init with the rect for the target
    rects = [target_coords]
    num_extra_objects = random.randint(0, MAX_EXTRA_OBJECTS)
    for _ in range(num_extra_objects):
        found_location = False
        for dummy in range(util.MAX_TRIES):
            obj_def = util.finalize_object_definition(random.choice(all_obj_defs))
            location = geometry.calc_obj_pos(performer_position, rects, obj_def)
            rect = rects[-1]
            rect_as_poly = shapely.geometry.Polygon([(point['x'], point['z']) for point in rect])
            # check intersection of rect_coords with line between target and performer
            visible_segment = shapely.geometry.LineString([(performer_position['x'],
                                                           performer_position['z']),
                                                           (target_x, target_z)])
            if rect_as_poly.intersects(visible_segment):
                # reject it
                rects.pop()
            else:
                found_location = True
                break
        if found_location:
            new_obj = util.instantiate_object(obj_def, location)
            scene['objects'].append(new_obj)


class InteractionPair(ABC):
    """Abstract base class for interaction pairs. This is analogous to the
    intphys quartets, but for interaction scenarios. See MCS-235.
    """

    def __init__(self, template: Dict[str, Any], find_path: bool):
        self._template = template
        self._find_path = find_path
        self._compute_performer_start()

    @abstractmethod
    def get_scenes(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        pass

    def _compute_performer_start(self) -> None:
        """Set the starting location (position & rotation) for the performer
        (_performer_start). This default implementation chooses a
        random location.
        """
        if getattr(self, '_performer_start', None) is None:
            self._performer_start = {
                'position': {
                    'x': round(random.uniform(PERFORMER_BOUNDS[0][0], PERFORMER_BOUNDS[0][1]), geometry.POSITION_DIGITS),
                    'y': 0,
                    'z': round(random.uniform(PERFORMER_BOUNDS[1][0], PERFORMER_BOUNDS[1][1]), geometry.POSITION_DIGITS)
                },
                'rotation': {
                    'y': geometry.random_rotation()
                }
            }

    def _get_empty_scene(self) -> Dict[str, Any]:
        scene = copy.deepcopy(self._template)
        scene['performerStart'] = self._performer_start
        return scene


class ImmediatelyVisiblePair(InteractionPair):
    """(1A) The Target Object is immediately visible (starting in view of
    the camera) OR (1B) behind the camera (must rotate to see the
    object). For each pair, the object may or may not be inside a
    container (like a box). See MCS-232.
    """

    def __init__(self, template: Dict[str, Any], find_path: bool):
        super(ImmediatelyVisiblePair, self).__init__(template, find_path)
        logging.debug(f'performerStart={self._performer_start}')

    def _get_locations(self, target_def: Dict[str, Any]) -> \
            Optional[Tuple[Dict[str, Any], Dict[str, Any]]]:
        # place target object in scene 1 right in front of the performer
        for _ in range(util.MAX_TRIES):
            in_front_location = geometry.\
                get_location_in_front_of_performer(self._performer_start, target_def)
            if in_front_location is not None:
                break
        if in_front_location is None:
            return None

        # place target object in scene 2 behind the performer
        for _ in range(util.MAX_TRIES):
            behind_location = geometry.\
                get_location_behind_performer(self._performer_start, target_def)
            if behind_location is not None:
                break
        if behind_location is None:
            return None

        return in_front_location, behind_location

    def get_scenes(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        # choose target object
        target_def = util.finalize_object_definition(random.choice(objects.get_all_object_defs()))
        for _ in range(util.MAX_TRIES):
            locations = self._get_locations(target_def)
            if locations is not None:
                break
            self._performer_start = None
            self._compute_performer_start()
        if locations is None:
            raise exceptions.SceneException('could not place performer with objects in front and behind')
        in_front_location, behind_location = locations

        scene1 = self._get_empty_scene()
        target = util.instantiate_object(target_def, in_front_location)
        scene1['objects'] = [target]
        add_objects(target, self._performer_start['position'], scene1)

        scene2 = self._get_empty_scene()
        target2 = copy.deepcopy(target)
        move_to_location(target_def, target2, behind_location)
        scene2['objects'] = [target2]
        add_objects(target, self._performer_start['position'], scene2)
        return scene1, scene2


class ImmediatelyVisibleSimilarPair(InteractionPair):
    """(6A) The Target Object is positioned immediately visible and a
    Similar Object is not immediately visible OR (6B) the Target
    Object is positioned not immediately visible and a Similar Object
    is immediately visible. For each pair, the objects may or may not
    be inside identical containers, but only if the container is big
    enough to hold both individually; otherwise, no container will be
    used in that pair. See MCS-233.
    """

    def __init__(self, template: Dict[str, Any], find_path: bool):
        super(ImmediatelyVisibleSimilarPair, self).__init__(template, find_path)
        logging.debug(f'performerStart={self._performer_start}')

    def _contained_in_front_and_back(self, container_def: Dict[str, Any],
                                     front_obj: Dict[str, Any],
                                     back_obj: Dict[str, Any]) -> \
                                     Optional[Tuple[Dict[str, Any], Dict[str, Any]]]:
        in_front_location = geometry. \
            get_location_in_front_of_performer(self._performer_start, container_def)
        behind_location = geometry. \
            get_location_behind_performer(self._performer_start, container_def)
        front_obj_container = util.instantiate_object(container_def, in_front_location)
        index, angles = containers.how_can_contain(container_def, front_obj)
        if index is None:
            return None
        containers.put_object_in_container(front_obj, front_obj_container, container_def, index, angles[0])
        back_obj_container = util.instantiate_object(container_def, behind_location)
        index, angles = containers.how_can_contain(container_def, back_obj)
        if index is None:
            return None
        containers.put_object_in_container(back_obj, back_obj_container, container_def, index, angles[0])

        return front_obj_container, back_obj_container

    def _move_in_front_and_back(self, front_obj_def: Dict[str, Any],
                                front_obj: Dict[str, Any],
                                back_obj_def: Dict[str, Any],
                                back_obj: Dict[str, Any]) -> bool:
        in_front_location = geometry. \
            get_location_in_front_of_performer(self._performer_start, front_obj_def)
        behind_location = geometry. \
            get_location_behind_performer(self._performer_start, back_obj_def)
        if in_front_location is None or behind_location is None:
            return False
        move_to_location(front_obj_def, front_obj, in_front_location)
        move_to_location(back_obj_def, back_obj, behind_location)
        return True

    def get_scenes(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        scene1 = self._get_empty_scene()
        scene2 = self._get_empty_scene()
        is_contained = random.random() <= util.TARGET_CONTAINED_CHANCE
        done = False
        for _ in range(util.MAX_TRIES):
            target_def = util.finalize_object_definition(random.choice(objects.get_all_object_defs()))
            similar_def = util.finalize_object_definition(util.get_similar_definition(target_def))
            if is_contained:
                target = util.instantiate_object(target_def, geometry.ORIGIN_LOCATION)
                similar = util.instantiate_object(similar_def, geometry.ORIGIN_LOCATION)
                container_defs = containers.get_enclosable_container_defs((target, similar))
                if len(container_defs) == 0:
                    is_contained = False
                else:
                    container_def = util.finalize_object_definition(random.choice(container_defs))
                    maybe_containers = self._contained_in_front_and_back(container_def,
                                                                         target, similar)
                    if maybe_containers is None:
                        continue
                    target_container, similar_container = maybe_containers
                    scene1['objects'] = [target, similar, target_container, similar_container]

                    target2 = copy.deepcopy(target)
                    similar2 = copy.deepcopy(similar)
                    maybe_containers2 = self._contained_in_front_and_back(container_def,
                                                                          similar2, target2)
                    if maybe_containers2 is None:
                        continue
                    similar_container2, target_container2 = maybe_containers2
                    scene2['objects'] = [target2, similar2, target_container2, similar_container2]
                    done = True
                    break
            # not contained
            target = util.instantiate_object(target_def, geometry.ORIGIN_LOCATION)
            similar = util.instantiate_object(similar_def, geometry.ORIGIN_LOCATION)
            if not self._move_in_front_and_back(target_def, target, similar_def, similar):
                continue
            scene1['objects'] = [target, similar]

            target2 = copy.deepcopy(target)
            similar2 = copy.deepcopy(similar)
            if not self._move_in_front_and_back(similar_def, similar2, target_def, target2):
                continue
            scene2['objects'] = [target2, similar2]
            done = True
            break
        if not done:
            raise exceptions.SceneException('could not place target in front and similar behind')
        return scene1, scene2


class HiddenBehindPair(InteractionPair):
    """(2A) The Target Object is immediately visible OR (2B) is hidden
    behind a larger object that itself is immediately visible. For
    each pair, the object may or may not be inside a container (like a
    box). See MCS-239.
    """

    def __init__(self, template: Dict[str, Any], find_path: bool):
        super(HiddenBehindPair, self).__init__(template, find_path)

    def get_scenes(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        for _ in range(util.MAX_TRIES):
            target_def = util.finalize_object_definition(random.choice(objects.get_all_object_defs()))
            blocker_defs = geometry.get_wider_and_taller_defs(target_def)
            if blocker_defs is not None:
                break
        if blocker_defs is None:
            raise exceptions.SceneException('could not get a target and blocker')
        blocker_def, blocker_angle = random.choice(blocker_defs)
        blocker_def = util.finalize_object_definition(blocker_def)

        scene1 = self._get_empty_scene()
        # place target object in scene 1 right in front of the performer
        for _ in range(util.MAX_TRIES):
            in_front_location = geometry.get_location_in_front_of_performer(self._performer_start, target_def)
            if in_front_location is not None:
                break
        if in_front_location is None:
            raise exceptions.SceneException('could not place target in front of performer')
        target = util.instantiate_object(target_def, in_front_location)
        scene1['objects'] = [target]

        # place blocker right in front of performer in scene 2
        for _ in range(util.MAX_TRIES):
            in_front_location = geometry.get_location_in_front_of_performer(self._performer_start, blocker_def,
                                                                            lambda: blocker_angle)
            if in_front_location is not None:
                break
        if in_front_location is None:
            raise exceptions.SceneException('could not place blocker in front of performer')
        # Rotate blocker to be "facing" the performer (accounting for
        # blocker_angle). There is a chance that this rotation could
        # cause the blocker to intersect the wall of the room, because
        # it's different from the rotation returned by
        # get_location_in_front_of_performer (which does check for
        # that). But it seems pretty unlikely.
        angle = self._performer_start['rotation']['y']
        in_front_location['rotation']['y'] = angle + blocker_angle
        blocker = util.instantiate_object(blocker_def, in_front_location)
        occluded_location = geometry.get_adjacent_location_on_side(target_def,
                                                                   blocker,
                                                                   self._performer_start['position'],
                                                                   geometry.Side.BACK)
        if occluded_location is None:
            raise exceptions.SceneException('could not place target behind blocker')
        target2 = copy.deepcopy(target)
        move_to_location(target_def, target2, occluded_location)
        scene2 = self._get_empty_scene()
        scene2['objects'] = [target2, blocker]

        return scene1, scene2
    

class SimilarAdjacentPair(InteractionPair):
    """(3A) The Target Object is positioned normally, without a Similar
    Object in the scene, OR (3B) with a Similar Object in the scene,
    and directly adjacent to it. For each pair, the objects may or may
    not be inside a container, but only if the container is big enough
    to hold both together; otherwise, no container will be used in
    that pair.
    """

    def __init__(self, template: Dict[str, Any], find_path: bool):
        super(SimilarAdjacentPair, self).__init__(template, find_path)

    def get_scenes(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        target_def = util.finalize_object_definition(random.choice(objects.get_all_object_defs()))
        target_location = geometry.calc_obj_pos(self._performer_start['position'], [], target_def)
        target = util.instantiate_object(target_def, target_location)
        similar_def = util.finalize_object_definition(util.get_similar_definition(target))
        container = None
        if random.random() <= util.TARGET_CONTAINED_CHANCE:
            container_defs = objects.get_enclosed_containers().copy()
            random.shuffle(container_defs)
            for container_def in container_defs:
                placement = containers.can_contain_both(container_def, target_def, similar_def)
                if placement is not None:
                    break
            if placement is not None:
                container_def, index, orientation, rot_a, rot_b = placement
                container_def = util.finalize_object_definition(container_def)
                container_location = geometry. \
                    calc_obj_pos(self._performer_start['position'], [], container_def)
                container = util.instantiate_object(container_def, container_location)
                containers.put_object_in_container(target, container, container_def, index, rot_a)
        scene1 = self._get_empty_scene()
        scene1['objects'] = [target] if container is None else [target, container]

        similar_location = geometry. \
            get_adjacent_location(similar_def, target,
                                  self._performer_start['position'])
        if similar_location is None:
            raise exceptions.SceneException('could not place similar object adjacent to target')
        similar = util.instantiate_object(similar_def, similar_location)
        scene2 = self._get_empty_scene()
        if container is None:
            scene2['objects'] = [target, similar]
        else:
            target2 = copy.deepcopy(target)
            containers.put_objects_in_container(target2, similar, container,
                                                container_def, index, orientation,
                                                rot_a, rot_b)
            scene2['objects'] = [target2, similar, container]

        return scene1, scene2


class SimilarFarPair(InteractionPair):
    def __init__(self, template: Dict[str, Any], find_path: bool):
        super(SimilarFarPair, self).__init__(template, find_path)

    def get_scenes(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        target_def = util.finalize_object_definition(random.choice(objects.get_all_object_defs()))
        target = util.instantiate_object(target_def, geometry.ORIGIN_LOCATION)
        similar_def = util.finalize_object_definition(util.get_similar_definition(target))
        scene1 = self._get_empty_scene()
        scene2 = self._get_empty_scene()
        container = None
        performer_position = self._performer_start['position']
        if random.random() <= util.TARGET_CONTAINED_CHANCE:
            container_defs = containers.get_enclosable_container_defs((target_def, similar_def))
            if len(container_defs) > 0:
                container_def = util.finalize_object_definition(random.choice(container_defs))
                container_location = geometry. \
                    calc_obj_pos(performer_position, [], container_def)
                container = util.instantiate_object(container_def, container_location)
                containers.put_object_in_container(target, container, container_def, 0)
                scene1['objects'] = [target, container]
                similar = util.instantiate_object(similar_def, geometry.ORIGIN_LOCATION)
                container2 = instantiate_away_from(container_def, performer_position, container)
                # Should be impossible for this to fail with normal
                # objects in our room, but just in case...
                if container2 is None:
                    raise exceptions.SceneException('could not place second container away from first')
                containers.put_object_in_container(similar, container2, container_def, 0)
                scene2['objects'] = [target, similar, container, container2]
        if container is None:
            target_location = geometry.calc_obj_pos(performer_position, [], target_def)
            move_to_location(target_def, target, target_location)
            similar = instantiate_away_from(similar_def, performer_position, target)
            # Should be impossible for this to fail with normal
            # objects in our room, but just in case...
            if similar is None:
                raise exceptions.SceneException('could not place similar object away from target')
            scene1['objects'] = [target]
            scene2['objects'] = [target, similar]
        return scene1, scene2


class SimilarAdjacentFarPair(InteractionPair):
    """(5A) The Target Object is positioned directly adjacent to a Similar
    Object OR (5B) far away from a Similar Object. For each pair, the
    objects may or may not be inside identical containers, but only if
    the container is big enough to hold both together; otherwise, no
    container will be used in that pair.
    """

    def __init__(self, template: Dict[str, Any], find_path: bool):
        super(SimilarAdjacentFarPair, self).__init__(template, find_path)

    def get_scenes(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        target_def = util.finalize_object_definition(random.choice(objects.get_all_object_defs()))
        target = util.instantiate_object(target_def, geometry.ORIGIN_LOCATION)
        similar_def = util.finalize_object_definition(util.get_similar_definition(target))
        scene1 = self._get_empty_scene()
        scene2 = self._get_empty_scene()
        placement = None
        performer_position = self._performer_start['position']
        if random.random() <= util.TARGET_CONTAINED_CHANCE:
            container_defs = objects.get_enclosed_containers().copy()
            random.shuffle(container_defs)
            for container_def in container_defs:
                container_def = util.finalize_object_definition(container_def)
                placement = containers.can_contain_both(container_def, target_def, similar_def)
                if placement is not None:
                    break
            if placement is not None:
                container_def, index, orientation, rot_a, rot_b = placement
                similar = util.instantiate_object(similar_def, geometry.ORIGIN_LOCATION)
                container_location = geometry. \
                    calc_obj_pos(performer_position, [], container_def)
                container = util.instantiate_object(container_def, container_location)
                containers.put_objects_in_container(target, similar, container,
                                                    container_def, index, orientation,
                                                    rot_a, rot_b)
                scene1['objects'] = [target, similar, container]

                # scene 2
                target_container_loc = geometry.calc_obj_pos(performer_position, [], container_def)
                target_container = util.instantiate_object(container_def, target_container_loc)
                target2 = util.instantiate_object(target_def, geometry.ORIGIN_LOCATION)
                containers.put_object_in_container(target2, target_container, container_def, index, rot_a)

                similar_container = instantiate_away_from(container_def, performer_position, target_container)
                similar2 = util.instantiate_object(target_def, geometry.ORIGIN_LOCATION)
                containers.put_object_in_container(similar2, similar_container, container_def, index, rot_b)
                scene2['objects'] = [target2, similar2, target_container, similar_container]
        if placement is None:
            # Decided not to use a container or couldn't find one that
            # could hold the target & similar objects.
            similar_location = geometry.get_adjacent_location(similar_def, target,
                                                              performer_position)
            similar = util.instantiate_object(similar_def, similar_location)
            scene1['objects'] = [target, similar]

            # scene 2
            target2_location = geometry.calc_obj_pos(performer_position, [], target_def)
            target2 = util.instantiate_object(target_def, target2_location)
            similar2 = instantiate_away_from(similar_def, performer_position, target2)
            scene2['objects'] = [target2, similar2]

        return scene1, scene2


class SimilarAdjacentContainedPair(InteractionPair):
    """(8A) The Target Object is positioned adjacent to a Similar Object,
    but the Similar Object is inside a container OR (8B) the Target
    Object is positioned adjacent to a Similar Object, but the Target
    Object is inside a container. See MCS-238.
    """

    def __init__(self, template: Dict[str, Any], find_path: bool):
        super(SimilarAdjacentContainedPair, self).__init__(template, find_path)

    def get_scenes(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        for _ in range(util.MAX_TRIES):
            target_def = util.finalize_object_definition(random.choice(objects.get_all_object_defs()))
            target_location = geometry.calc_obj_pos(self._performer_start['position'], [], target_def)
            target = util.instantiate_object(target_def, target_location)
            similar_def = util.get_similar_definition(target)
            similar = util.instantiate_object(similar_def, geometry.ORIGIN_LOCATION)
            # find a container big enough for both of them
            valid_containments = containers.get_enclosable_containments((target, similar))
            if len(valid_containments) > 0:
                break
        if len(valid_containments) == 0:
            raise exceptions.SceneException(f'failed to find target and/or similar object that will fit in something')
        containment = random.choice(valid_containments)
        container_def, area_index, angles = containment
        container_def = util.finalize_object_definition(container_def)
        container_location = geometry.get_adjacent_location(container_def,
                                                            target,
                                                            self._performer_start['position'])
        container = util.instantiate_object(container_def, container_location)

        containers.put_object_in_container(similar, container, container_def, area_index, angles[1])

        scene1 = self._get_empty_scene()
        scene1['objects'] = [target, similar, container]

        target2 = copy.deepcopy(target)
        container2 = copy.deepcopy(container)
        containers.put_object_in_container(target2, container2, container_def, area_index, angles[0])
        similar2 = copy.deepcopy(similar)
        del similar2['locationParent']
        similar2_location = geometry.get_adjacent_location(similar_def,
                                                           container2,
                                                           self._performer_start['position'])
        move_to_location(similar_def, similar2, similar2_location)
        scene2 = self._get_empty_scene()
        scene2['objects'] = [target2, similar2, container2]

        return scene1, scene2


_INTERACTION_PAIR_CLASSES = [
    HiddenBehindPair,
    ImmediatelyVisiblePair,
    ImmediatelyVisibleSimilarPair,
    SimilarAdjacentPair,
    SimilarFarPair,
    SimilarAdjacentContainedPair
]


def get_pair_class() -> Type[InteractionPair]:
    return random.choice(_INTERACTION_PAIR_CLASSES)
