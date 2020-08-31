import copy

import shapely
from shapely import affinity

import geometry
import objects
import pairs
import util


MAX_DIMENSION = max(
    geometry.ROOM_X_MAX -
    geometry.ROOM_X_MIN,
    geometry.ROOM_Z_MAX -
    geometry.ROOM_Z_MIN)
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
    },
    'paintingMaterial': 'test_paint_material',
    'paintingColors': ['test_paint_color']
}


def get_parent(object_instance, object_list):
    parent_id = object_instance['locationParent']
    parent = next((o for o in object_list if o['id'] == parent_id))
    return parent


def verify_confusor(target, confusor):
    assert target['id'] != confusor['id']
    is_same_color = set(target['color']) == set(confusor['color'])
    is_same_shape = target['shape'] == confusor['shape']
    is_same_size = target['size'] == confusor['size'] and \
        (target['dimensions']['x'] - util.MAX_SIZE_DIFFERENCE) <= \
        confusor['dimensions']['x'] <= \
        (target['dimensions']['x'] + util.MAX_SIZE_DIFFERENCE) and \
        (target['dimensions']['y'] - util.MAX_SIZE_DIFFERENCE) <= \
        confusor['dimensions']['y'] <= \
        (target['dimensions']['y'] + util.MAX_SIZE_DIFFERENCE) and \
        (target['dimensions']['z'] - util.MAX_SIZE_DIFFERENCE) <= \
        confusor['dimensions']['z'] <= \
        (target['dimensions']['z'] + util.MAX_SIZE_DIFFERENCE)
    if (
        (not is_same_color and not is_same_shape) or
        (not is_same_color and not is_same_size) or
        (not is_same_shape and not is_same_size) or
        (is_same_color and is_same_shape and is_same_size)
    ):
        print(
            f'[ERROR] CONFUSOR SHOULD BE THE SAME AS THE TARGET IN ALL '
            f'EXCEPT ONE: color={is_same_color} shape={is_same_shape} '
            f'size={is_same_size}\ntarget={target}\nconfusor={confusor}')
        return False
    return True


def verify_immediately_visible(
        performer_start, object_list, target, name='target'):
    target_or_parent = get_parent(
        target, object_list) if 'locationParent' in target else target
    target_poly = geometry.get_bounding_polygon(target_or_parent)

    view_line = shapely.geometry.LineString([[0, 0], [0, MAX_DIMENSION]])
    view_line = affinity.rotate(
        view_line, -performer_start['rotation']['y'], origin=(0, 0)
    )
    view_line = affinity.translate(
        view_line,
        performer_start['position']['x'],
        performer_start['position']['z'])

    if not target_poly.intersection(view_line):
        print(f'[ERROR] {name.upper()} SHOULD BE VISIBLE IN FRONT OF '
              f'PERFORMER:\n{name}={target_or_parent}\n'
              f'performer_start={performer_start}')
        return False

    ignore_id_list = [target['id'], target_or_parent['id']]
    for object_instance in object_list:
        if object_instance['id'] not in ignore_id_list:
            object_poly = geometry.get_bounding_polygon(object_instance)
            if geometry.does_fully_obstruct_target(
                performer_start['position'], target_or_parent, object_poly
            ):
                print(
                    f'[ERROR] NON-{name.upper()} SHOULD NOT OBSTRUCT '
                    f'{name.upper()}:\n{name}={target_or_parent}\n'
                    f'non-{name}={object_instance}'
                    f'\nperformer_start={performer_start}'
                )
                return False

    return True


def verify_not_immediately_visible(
        performer_start, object_list, target, name='target'):
    result = verify_immediately_visible(
        performer_start, object_list, target, name)
    if result:
        target_or_parent = get_parent(
            target, object_list) if 'locationParent' in target else target
        print(f'[ERROR] {name.upper()} SHOULD NOT BE VISIBLE IN FRONT OF '
              f'PERFORMER:\n{name}={target_or_parent}\n'
              f'performer_start={performer_start}')
    return not result


def verify_obstructor(goal, scene, obstruct_vision=False):
    performer_start = goal.get_performer_start()
    target = goal.get_target_list()[0]
    obstructor = goal.get_obstructor_list()[0]
    dimensions = (
        obstructor['closedDimensions']
        if 'closedDimensions' in obstructor
        else obstructor['dimensions']
    )

    is_bigger = (
        target['dimensions']['x'] <= dimensions['x'] or
        target['dimensions']['z'] <= dimensions['z']
    ) and (not obstruct_vision or target['dimensions']['y'] <= dimensions['y'])
    if not is_bigger:
        print(
            f'[ERROR] OBSTRUCTOR SHOULD BE BIGGER THAN TARGET:\n'
            f'target={target}\nobstructor={obstructor}')
        return False

    obstructor_poly = geometry.get_bounding_polygon(obstructor)
    if not geometry.does_fully_obstruct_target(
            performer_start['position'], target, obstructor_poly):
        print(
            f'[ERROR] OBSTRUCTOR SHOULD OBSTRUCT TARGET:\ntarget={target}\n'
            f'obstructor={obstructor}')
        return False

    object_list = scene['objects']
    ignore_id_list = [
        obstructor['id'],
        target['id'],
        target['locationParent'] if 'locationParent' in target else None]
    for object_instance in object_list:
        if object_instance['id'] not in ignore_id_list:
            object_poly = geometry.get_bounding_polygon(object_instance)
            if geometry.does_fully_obstruct_target(
                    performer_start['position'], target, object_poly):
                print(
                    f'[ERROR] NON-OBSTRUCTOR SHOULD NOT OBSTRUCT TARGET:\n'
                    f'object={object_instance}\ntarget={target}\n'
                    f'performer_start={performer_start}')
                return False

    return True


def verify_same_object_list(
        name, object_list_1, object_list_2, ignore_id_list):
    modified_object_list_1 = [
        obj for obj in object_list_1 if obj['id'] not in ignore_id_list]
    modified_object_list_2 = [
        obj for obj in object_list_2 if obj['id'] not in ignore_id_list]
    if len(modified_object_list_1) != len(modified_object_list_2):
        print(f'[ERROR] {name.upper()} LIST SHOULD BE THE SAME LENGTH')
        return False
    for index in range(len(modified_object_list_1)):
        object_instance_1 = modified_object_list_1[index]
        object_instance_2 = modified_object_list_2[index]
        if object_instance_1 != object_instance_2:
            print(
                f'[ERROR] {name.upper()} SHOULD BE THE SAME:\n{name}_1='
                f'{object_instance_1}\n{name}_2={object_instance_2}')
            return False
    return True


def verify_same_object(name, object_1, object_2, difference_list):
    key_set_1 = set(object_1.keys())
    key_set_2 = set(object_2.keys())
    for key in key_set_1.union(key_set_2):
        if key in difference_list:
            if (key in object_1 and key not in object_2) or (
                    key not in object_1 and key in object_2):
                pass
            elif (key not in object_1 and key not in object_2) or object_1[
                key
            ] == object_2[key]:
                print(
                    f'[ERROR] "{key}" PROPERTY SHOULD NOT BE THE SAME:\n'
                    f'{name}_1={object_1}\n{name}_2={object_2}')
                return False
        else:
            if (
                key not in object_1 or
                key not in object_2 or
                object_1[key] != object_2[key]
            ):
                print(
                    f'[ERROR] "{key}" PROPERTY SHOULD BE THE SAME:\n'
                    f'{name}_1={object_1}\n{name}_2={object_2}')
                return False
    return True


def verify_pair(pair, scene_1, scene_2, target_same_position=True,
                confusor_same_position=True,
                target_parent_same_position=True,
                confusor_parent_same_position=True, target_parent_same=True,
                confusor_parent_same=True):
    assert scene_1
    assert scene_2

    # Ensure the performer start in each scene is the same.
    performer_start_1 = pair._goal_1.get_performer_start()
    assert performer_start_1
    performer_start_2 = pair._goal_2.get_performer_start()
    assert performer_start_2
    if performer_start_1 != performer_start_2:
        print(
            f'[ERROR] performer_start SHOULD BE THE SAME: '
            f'{performer_start_1} != {performer_start_2}')
        return False

    performer_start_poly = geometry.rect_to_poly(
        geometry.find_performer_rect(
            performer_start_1['position']))
    for object_instance in scene_1['objects']:
        object_poly = geometry.get_bounding_polygon(object_instance)
        if object_poly.intersects(performer_start_poly):
            print(
                f'[ERROR] performer_start SHOULD NOT BE INSIDE AN OBJECT:\n'
                f'performer_start_poly={performer_start_poly}\n'
                f'object_poly={object_poly}')
            return False

    # Ensure the target object in each scene is the same, except for expected
    # differences.
    target_1 = pair._goal_1.get_target_list()[0]
    assert target_1
    print(f'[DEBUG] target_1={target_1}')
    target_2 = pair._goal_2.get_target_list()[0]
    assert target_2
    print(f'[DEBUG] target_2={target_2}')
    if not verify_same_object(
        'target',
        target_1,
        target_2,
        ([] if target_same_position else ['shows']) +
        ([] if target_parent_same else ['locationParent'])
    ):
        return False

    # If the target in each scene has a parent, ensure each target's parent is
    # the same.
    target_parent_1 = get_parent(
        target_1, scene_1['objects']) if 'locationParent' in target_1 else None
    print(f'[DEBUG] target_parent_1={target_parent_1}')
    target_parent_2 = get_parent(
        target_2, scene_2['objects']) if 'locationParent' in target_2 else None
    print(f'[DEBUG] target_parent_2={target_parent_2}')
    if target_parent_1 and target_parent_2 and target_parent_same:
        if not verify_same_object(
            'target_parent',
            target_parent_1,
            target_parent_2,
            [] if target_parent_same_position else ['shows']
        ):
            return False

    # If a scene has a confusor, verify that it's a confusor of the target.
    confusor_1 = pair._goal_1.get_confusor_list()[0] if len(
        pair._goal_1.get_confusor_list()) > 0 else None
    print(f'[DEBUG] confusor_1={confusor_1}')
    if confusor_1 and not verify_confusor(target_1, confusor_1):
        return False
    confusor_2 = pair._goal_2.get_confusor_list()[0] if len(
        pair._goal_2.get_confusor_list()) > 0 else None
    print(f'[DEBUG] confusor_2={confusor_2}')
    if confusor_2 and not verify_confusor(target_2, confusor_2):
        return False
    if confusor_1 and confusor_2:
        if not verify_same_object(
            'confusor',
            confusor_1,
            confusor_2,
            ([] if confusor_same_position else ['shows']) +
            ([] if confusor_parent_same else ['locationParent'])
        ):
            return False

    # If each scene has a confusor with a parent, ensure each confusor's
    # parent is the same.
    confusor_parent_1 = (
        get_parent(confusor_1, scene_1['objects'])
        if (confusor_1 and 'locationParent' in confusor_1)
        else None
    )
    print(f'[DEBUG] confusor_parent_1={confusor_parent_1}')
    confusor_parent_2 = (
        get_parent(confusor_2, scene_2['objects'])
        if (confusor_2 and 'locationParent' in confusor_2)
        else None
    )
    print(f'[DEBUG] confusor_parent_2={confusor_parent_2}')
    if confusor_parent_1 and confusor_parent_2 and confusor_parent_same:
        if not verify_same_object(
            'confusor_parent',
            confusor_parent_1,
            confusor_parent_2,
            [] if confusor_parent_same_position else ['shows']
        ):
            return False

    target_parent_id = (  # noqa: F841
        target_parent_1['id']
        if target_parent_1
        else (target_parent_2['id'] if target_parent_2 else None)
    )
    confusor_id = (  # noqa: F841
        confusor_1['id']
        if confusor_1
        else (confusor_2['id'] if confusor_2 else None)
    )
    confusor_parent_id = (  # noqa: F841
        confusor_parent_1['id']
        if confusor_parent_1
        else (confusor_parent_2['id'] if confusor_parent_2 else None)
    )

    # Ignore the IDs of the target, confusor, and target/confusor parent,
    # because they may change across the scenes.
    ignore_id_list = [object_id for object_id in [
        target_1['id'],
        target_2['id'],
        target_parent_1['id'] if target_parent_1 else None,
        target_parent_2['id'] if target_parent_2 else None,
        confusor_1['id'] if confusor_1 else None,
        confusor_2['id'] if confusor_2 else None,
        confusor_parent_1['id'] if confusor_parent_1 else None,
        confusor_parent_2['id'] if confusor_parent_2 else None
    ] if object_id]

    # Ensure the random distractors are the same across the scenes.
    distractor_list_1 = pair._goal_1.get_distractor_list()
    distractor_list_2 = pair._goal_2.get_distractor_list()
    if not verify_same_object_list(
        'distractor', distractor_list_1, distractor_list_2, ignore_id_list
    ):
        return False

    return True


def test_Pair1():
    pair = pairs.Pair1(BODY_TEMPLATE)
    assert pair
    scene_1, scene_2 = pair.get_scenes()
    containerize = (
        pair._options.target_containerize == pairs.BoolPairOption.YES_YES
    )
    # The target's position is the same if it's in a box because only its box
    # will have a different position.
    assert verify_pair(
        pair,
        scene_1,
        scene_2,
        target_same_position=containerize,
        target_parent_same_position=False)

    target_1 = pair._goal_1.get_target_list()[0]
    target_2 = pair._goal_2.get_target_list()[0]
    if containerize:
        assert verify_immediately_visible(
            pair._goal_1.get_performer_start(),
            scene_1['objects'],
            get_parent(target_1, scene_1['objects'])
        )
        assert verify_not_immediately_visible(
            pair._goal_2.get_performer_start(),
            scene_2['objects'],
            get_parent(target_2, scene_2['objects'])
        )
    else:
        assert verify_immediately_visible(
            pair._goal_1.get_performer_start(),
            scene_1['objects'],
            target_1)
        assert verify_not_immediately_visible(
            pair._goal_2.get_performer_start(), scene_2['objects'], target_2)

    assert len(pair._goal_1.get_confusor_list()) == 0
    assert len(pair._goal_2.get_confusor_list()) == 0
    assert len(pair._goal_1.get_obstructor_list()) == 0
    assert len(pair._goal_2.get_obstructor_list()) == 0


def test_Pair2():
    pair = pairs.Pair2(BODY_TEMPLATE)
    assert pair
    scene_1, scene_2 = pair.get_scenes()
    containerize = (
        pair._options.target_containerize == pairs.BoolPairOption.YES_YES
    )
    assert verify_pair(pair, scene_1, scene_2)

    target_1 = pair._goal_1.get_target_list()[0]
    target_2 = pair._goal_2.get_target_list()[0]
    if containerize:
        assert verify_immediately_visible(
            pair._goal_1.get_performer_start(),
            scene_1['objects'],
            get_parent(target_1, scene_1['objects'])
        )
        assert verify_not_immediately_visible(
            pair._goal_2.get_performer_start(),
            scene_2['objects'],
            get_parent(target_2, scene_2['objects'])
        )
    else:
        assert verify_immediately_visible(
            pair._goal_1.get_performer_start(),
            scene_1['objects'],
            target_1)
        assert verify_not_immediately_visible(
            pair._goal_2.get_performer_start(), scene_2['objects'], target_2)

    assert len(pair._goal_1.get_confusor_list()) == 0
    assert len(pair._goal_2.get_confusor_list()) == 0
    assert len(pair._goal_1.get_obstructor_list()) == 0
    assert len(pair._goal_2.get_obstructor_list()) == 1

    assert verify_obstructor(pair._goal_2, scene_2, obstruct_vision=True)


def test_Pair3():
    pair = pairs.Pair3(BODY_TEMPLATE)
    assert pair
    scene_1, scene_2 = pair.get_scenes()
    containerize = (
        pair._options.target_containerize == pairs.BoolPairOption.YES_YES
    )
    # The target's position is NOT the same if it's in a box because of how
    # the confusor's positioned next to it.
    assert verify_pair(
        pair,
        scene_1,
        scene_2,
        target_same_position=(
            not containerize))

    assert len(pair._goal_1.get_confusor_list()) == 0
    assert len(pair._goal_2.get_confusor_list()) == 1
    assert len(pair._goal_1.get_obstructor_list()) == 0
    assert len(pair._goal_2.get_obstructor_list()) == 0

    target_1 = pair._goal_1.get_target_list()[0]
    target_2 = pair._goal_2.get_target_list()[0]
    confusor_2 = pair._goal_2.get_confusor_list()[0]
    assert geometry.are_adjacent(target_2, confusor_2)
    if containerize:
        assert target_1['locationParent']
        assert target_2['locationParent'] == confusor_2['locationParent']
    else:
        assert 'locationParent' not in target_1
        assert 'locationParent' not in target_2
        assert 'locationParent' not in confusor_2


def test_Pair4():
    pair = pairs.Pair4(BODY_TEMPLATE)
    assert pair
    scene_1, scene_2 = pair.get_scenes()
    containerize = (
        pair._options.target_containerize == pairs.BoolPairOption.YES_YES
    )
    assert verify_pair(pair, scene_1, scene_2)

    assert len(pair._goal_1.get_confusor_list()) == 0
    assert len(pair._goal_2.get_confusor_list()) == 1
    assert len(pair._goal_1.get_obstructor_list()) == 0
    assert len(pair._goal_2.get_obstructor_list()) == 0

    target_1 = pair._goal_1.get_target_list()[0]
    target_2 = pair._goal_2.get_target_list()[0]
    confusor_2 = pair._goal_2.get_confusor_list()[0]
    if containerize:
        assert target_1['locationParent']
        assert target_2['locationParent'] != confusor_2['locationParent']
        assert not geometry.are_adjacent(
            get_parent(target_2, scene_2['objects']),
            get_parent(confusor_2, scene_2['objects'])
        )
    else:
        assert 'locationParent' not in target_1
        assert 'locationParent' not in target_2
        assert 'locationParent' not in confusor_2
        assert geometry.are_adjacent(target_2, confusor_2)


def test_Pair5():
    pair = pairs.Pair5(BODY_TEMPLATE)
    assert pair
    scene_1, scene_2 = pair.get_scenes()
    containerize = (
        pair._options.target_containerize == pairs.BoolPairOption.YES_YES
    )
    # The target's position is NOT the same if it's in a box because of how
    # the confusor's positioned next to it.
    assert verify_pair(
        pair,
        scene_1,
        scene_2,
        target_same_position=(not containerize),
        confusor_same_position=False,
        confusor_parent_same=False
    )

    assert len(pair._goal_1.get_confusor_list()) == 1
    assert len(pair._goal_2.get_confusor_list()) == 1
    assert len(pair._goal_1.get_obstructor_list()) == 0
    assert len(pair._goal_2.get_obstructor_list()) == 0

    target_1 = pair._goal_1.get_target_list()[0]
    target_2 = pair._goal_2.get_target_list()[0]
    confusor_1 = pair._goal_1.get_confusor_list()[0]
    confusor_2 = pair._goal_2.get_confusor_list()[0]
    assert geometry.are_adjacent(target_1, confusor_1)
    if containerize:
        assert target_1['locationParent'] == confusor_1['locationParent']
        assert target_2['locationParent'] != confusor_2['locationParent']
        assert not geometry.are_adjacent(
            get_parent(target_2, scene_2['objects']),
            get_parent(confusor_2, scene_2['objects'])
        )
    else:
        assert 'locationParent' not in target_1
        assert 'locationParent' not in target_2
        assert 'locationParent' not in confusor_1
        assert 'locationParent' not in confusor_2
        assert not geometry.are_adjacent(target_2, confusor_2)


def test_Pair6():
    pair = pairs.Pair6(BODY_TEMPLATE)
    assert pair
    scene_1, scene_2 = pair.get_scenes()
    containerize = (
        pair._options.target_containerize == pairs.BoolPairOption.YES_YES
    )
    # The object's position is the same if it's in a box because only its box
    # will have a different position.
    assert verify_pair(
        pair,
        scene_1,
        scene_2,
        target_same_position=containerize,
        confusor_same_position=containerize,
        target_parent_same_position=False,
        confusor_parent_same_position=False
    )

    assert len(pair._goal_1.get_confusor_list()) == 1
    assert len(pair._goal_2.get_confusor_list()) == 1
    assert len(pair._goal_1.get_obstructor_list()) == 0
    assert len(pair._goal_2.get_obstructor_list()) == 0

    target_1 = pair._goal_1.get_target_list()[0]
    target_2 = pair._goal_2.get_target_list()[0]
    confusor_1 = pair._goal_1.get_confusor_list()[0]
    confusor_2 = pair._goal_2.get_confusor_list()[0]
    if containerize:
        assert target_1['locationParent'] != confusor_1['locationParent']
        assert target_2['locationParent'] != confusor_2['locationParent']
        assert verify_immediately_visible(
            pair._goal_1.get_performer_start(),
            scene_1['objects'],
            get_parent(target_1, scene_1['objects'])
        )
        assert verify_not_immediately_visible(
            pair._goal_2.get_performer_start(),
            scene_2['objects'],
            get_parent(target_2, scene_2['objects'])
        )
        assert verify_not_immediately_visible(
            pair._goal_1.get_performer_start(),
            scene_1['objects'],
            get_parent(confusor_1, scene_1['objects']),
            'confusor'
        )
        assert verify_immediately_visible(
            pair._goal_2.get_performer_start(),
            scene_2['objects'],
            get_parent(confusor_2, scene_2['objects']),
            'confusor'
        )
    else:
        assert 'locationParent' not in target_1
        assert 'locationParent' not in target_2
        assert 'locationParent' not in confusor_1
        assert 'locationParent' not in confusor_2
        assert verify_immediately_visible(
            pair._goal_1.get_performer_start(),
            scene_1['objects'],
            target_1)
        assert verify_not_immediately_visible(
            pair._goal_2.get_performer_start(), scene_2['objects'], target_2)
        assert verify_not_immediately_visible(
            pair._goal_1.get_performer_start(),
            scene_1['objects'],
            confusor_1,
            'confusor'
        )
        assert verify_immediately_visible(
            pair._goal_2.get_performer_start(),
            scene_2['objects'],
            confusor_2,
            'confusor'
        )


def test_Pair7():
    pair = pairs.Pair7(BODY_TEMPLATE)
    assert pair
    scene_1, scene_2 = pair.get_scenes()
    # The target's position is the same if it's in a box because only its box
    # will have a different position.
    assert verify_pair(
        pair,
        scene_1,
        scene_2,
        confusor_same_position=False,
        target_parent_same_position=False)

    assert len(pair._goal_1.get_confusor_list()) == 1
    assert len(pair._goal_2.get_confusor_list()) == 1
    assert len(pair._goal_1.get_obstructor_list()) == 0
    assert len(pair._goal_2.get_obstructor_list()) == 0

    target_1 = pair._goal_1.get_target_list()[0]
    target_2 = pair._goal_2.get_target_list()[0]
    confusor_1 = pair._goal_1.get_confusor_list()[0]
    confusor_2 = pair._goal_2.get_confusor_list()[0]
    assert verify_not_immediately_visible(
        pair._goal_1.get_performer_start(),
        scene_1['objects'],
        confusor_1,
        'confusor'
    )
    assert verify_immediately_visible(
        pair._goal_2.get_performer_start(),
        scene_2['objects'],
        confusor_2,
        'confusor')
    assert 'locationParent' in target_1
    assert 'locationParent' in target_2
    assert 'locationParent' not in confusor_1
    assert 'locationParent' not in confusor_2
    assert verify_immediately_visible(
        pair._goal_1.get_performer_start(),
        scene_1['objects'],
        get_parent(target_1, scene_1['objects'])
    )
    assert verify_not_immediately_visible(
        pair._goal_2.get_performer_start(),
        scene_2['objects'],
        get_parent(target_2, scene_2['objects'])
    )


def test_Pair8():
    pair = pairs.Pair8(BODY_TEMPLATE)
    assert pair
    scene_1, scene_2 = pair.get_scenes()
    assert verify_pair(
        pair,
        scene_1,
        scene_2,
        target_same_position=False,
        target_parent_same=False)

    assert len(pair._goal_1.get_confusor_list()) == 1
    assert len(pair._goal_2.get_confusor_list()) == 1
    assert len(pair._goal_1.get_obstructor_list()) == 0
    assert len(pair._goal_2.get_obstructor_list()) == 0

    target_1 = pair._goal_1.get_target_list()[0]
    target_2 = pair._goal_2.get_target_list()[0]
    confusor_1 = pair._goal_1.get_confusor_list()[0]
    confusor_2 = pair._goal_2.get_confusor_list()[0]
    assert geometry.are_adjacent(target_1, confusor_1)
    assert geometry.are_adjacent(
        get_parent(
            target_2,
            scene_2['objects']),
        confusor_2)
    assert 'locationParent' not in target_1
    assert 'locationParent' in target_2
    assert 'locationParent' not in confusor_1
    assert 'locationParent' not in confusor_2


def test_Pair9():
    pair = pairs.Pair9(BODY_TEMPLATE)
    assert pair
    scene_1, scene_2 = pair.get_scenes()
    containerize = (
        pair._options.target_containerize == pairs.BoolPairOption.YES_YES
    )
    assert verify_pair(pair, scene_1, scene_2)

    target_1 = pair._goal_1.get_target_list()[0]
    target_2 = pair._goal_2.get_target_list()[0]
    if containerize:
        assert verify_immediately_visible(
            pair._goal_1.get_performer_start(),
            scene_1['objects'],
            get_parent(target_1, scene_1['objects'])
        )
        assert verify_not_immediately_visible(
            pair._goal_2.get_performer_start(),
            scene_2['objects'],
            get_parent(target_2, scene_2['objects'])
        )
    else:
        assert verify_immediately_visible(
            pair._goal_1.get_performer_start(),
            scene_1['objects'],
            target_1)
        assert verify_not_immediately_visible(
            pair._goal_2.get_performer_start(), scene_2['objects'], target_2)

    assert len(pair._goal_1.get_confusor_list()) == 0
    assert len(pair._goal_2.get_confusor_list()) == 0
    assert len(pair._goal_1.get_obstructor_list()) == 0
    assert len(pair._goal_2.get_obstructor_list()) == 1

    assert verify_obstructor(pair._goal_2, scene_2, obstruct_vision=False)


def test_Pair11():
    pair = pairs.Pair11(BODY_TEMPLATE)
    assert pair
    scene_1, scene_2 = pair.get_scenes()
    assert verify_pair(
        pair,
        scene_1,
        scene_2,
        target_same_position=False,
        confusor_same_position=False)

    target_1 = pair._goal_1.get_target_list()[0]
    target_2 = pair._goal_2.get_target_list()[0]
    confusor_1 = pair._goal_1.get_confusor_list()[0]
    confusor_2 = pair._goal_2.get_confusor_list()[0]
    assert verify_immediately_visible(
        pair._goal_1.get_performer_start(),
        scene_1['objects'],
        target_1)
    assert verify_not_immediately_visible(
        pair._goal_2.get_performer_start(),
        scene_2['objects'],
        target_2)
    """
    assert verify_immediately_visible(pair._goal_1.get_performer_start(),
                                      scene_1['objects'], confusor_1,
                                      'confusor')
    assert verify_not_immediately_visible(pair._goal_2.get_performer_start(),
                                          scene_2['objects'], confusor_2,
                                          'confusor')
    """
    assert geometry.are_adjacent(target_1, confusor_1)
    assert geometry.are_adjacent(target_2, confusor_2)
    assert 'locationParent' not in target_1
    assert 'locationParent' not in target_2
    assert 'locationParent' not in confusor_1
    assert 'locationParent' not in confusor_2


def test_Pair2_sofa_target_sofa_obstructor():
    """See MCS-314"""
    sofa = util.finalize_object_definition(objects.get('SOFA_1'))
    sofa = util.finalize_object_materials_and_colors(sofa)[0]
    # Same SceneOptions as Pair2
    scene_options = pairs.SceneOptions(
        target_definition=sofa,
        target_location=pairs.TargetLocationPairOption.FRONT_FRONT,
        obstructor=pairs.ObstructorPairOption.NONE_VISION,
        obstructor_definition=copy.deepcopy(sofa)
    )
    pair = pairs.InteractionPair(
        2,
        BODY_TEMPLATE,
        'Traversal',
        False,
        scene_options)
    assert pair
    scene_1, scene_2 = pair.get_scenes()
    assert verify_pair(pair, scene_1, scene_2)

    target_1 = pair._goal_1.get_target_list()[0]
    target_2 = pair._goal_2.get_target_list()[0]
    assert verify_immediately_visible(
        pair._goal_1.get_performer_start(),
        scene_1['objects'],
        target_1)
    assert verify_not_immediately_visible(
        pair._goal_2.get_performer_start(),
        scene_2['objects'],
        target_2)

    assert len(pair._goal_1.get_confusor_list()) == 0
    assert len(pair._goal_2.get_confusor_list()) == 0
    assert len(pair._goal_1.get_obstructor_list()) == 0
    assert len(pair._goal_2.get_obstructor_list()) == 1

    assert verify_obstructor(pair._goal_2, scene_2, obstruct_vision=True)
