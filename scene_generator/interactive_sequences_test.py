import copy
import geometry
import objects
from interactive_goals import RetrievalGoal, TraversalGoal
from interactive_plans import BoolPlan, InteractivePlan, ObstructorPlan, \
    TargetLocationPlan, is_true
from interactive_sequences import WALL_DEPTH, WALL_HEIGHT, WALL_MAX_WIDTH, \
    WALL_MIN_WIDTH, WALL_Y, InteractiveSequence, InteractivePairFactory
import shapely
from shapely import affinity
import util


MAX_DIMENSION = max(
    geometry.ROOM_X_MAX - geometry.ROOM_X_MIN,
    geometry.ROOM_Z_MAX - geometry.ROOM_Z_MIN
)


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
    }
}


def test_generate_wall():
    sequence = InteractiveSequence(BODY_TEMPLATE, RetrievalGoal(),
                                   InteractivePlan('mock'))
    wall = sequence._create_interior_wall(
        'test_material',
        ['test_color_1', 'test_color_2'],
        geometry.ORIGIN_LOCATION,
        []
    )

    assert wall
    assert wall['id']
    assert wall['materials'] == ['test_material']
    assert wall['type'] == 'cube'
    assert wall['kinematic'] == 'true'
    assert wall['structure'] == 'true'
    assert wall['mass'] == 200
    assert wall['info'] == ['test_color_1', 'test_color_2']

    assert len(wall['shows']) == 1
    assert wall['shows'][0]['stepBegin'] == 0
    assert wall['shows'][0]['scale']['x'] >= WALL_MIN_WIDTH and \
        wall['shows'][0]['scale']['x'] <= WALL_MAX_WIDTH
    assert wall['shows'][0]['scale']['y'] == WALL_HEIGHT
    assert wall['shows'][0]['scale']['z'] == WALL_DEPTH
    assert wall['shows'][0]['rotation']['x'] == 0
    assert wall['shows'][0]['rotation']['y'] % 90 == 0
    assert wall['shows'][0]['rotation']['z'] == 0
    assert wall['shows'][0]['position']['x'] is not None
    assert wall['shows'][0]['position']['y'] == WALL_Y
    assert wall['shows'][0]['position']['z'] is not None
    assert wall['shows'][0]['boundingBox'] is not None

    assert 'hides' not in wall
    assert 'moves' not in wall
    assert 'rotates' not in wall
    assert 'teleports' not in wall

    player_rect = geometry.find_performer_rect(geometry.ORIGIN)
    player_poly = geometry.rect_to_poly(player_rect)
    wall_poly = geometry.rect_to_poly(wall['shows'][0]['boundingBox'])
    assert not wall_poly.intersects(player_poly)
    assert geometry.rect_within_room(wall['shows'][0]['boundingBox'])


def test_generate_wall_multiple():
    sequence = InteractiveSequence(BODY_TEMPLATE, RetrievalGoal(),
                                   InteractivePlan('mock'))
    wall_1 = sequence._create_interior_wall(
        'test_material',
        [],
        geometry.ORIGIN_LOCATION,
        []
    )
    wall_2 = sequence._create_interior_wall(
        'test_material',
        [],
        geometry.ORIGIN_LOCATION,
        [wall_1['shows'][0]['boundingBox']]
    )
    wall_1_poly = geometry.rect_to_poly(wall_1['shows'][0]['boundingBox'])
    wall_2_poly = geometry.rect_to_poly(wall_2['shows'][0]['boundingBox'])
    assert not wall_1_poly.intersects(wall_2_poly)


def test_generate_wall_with_bounds_list():
    bounds = [{'x': 4, 'y': 0, 'z': 4}, {'x': 4, 'y': 0, 'z': 1},
              {'x': 1, 'y': 0, 'z': 1}, {'x': 1, 'y': 0, 'z': 4}]
    sequence = InteractiveSequence(BODY_TEMPLATE, RetrievalGoal(),
                                   InteractivePlan('mock'))
    wall = sequence._create_interior_wall(
        'test_material',
        [],
        geometry.ORIGIN_LOCATION,
        [bounds]
    )
    poly = geometry.rect_to_poly(bounds)
    wall_poly = geometry.rect_to_poly(wall['shows'][0]['boundingBox'])
    assert not wall_poly.intersects(poly)


def test_generate_wall_with_target_list():
    bounds = [{'x': 4, 'y': 0, 'z': 4}, {'x': 4, 'y': 0, 'z': 3},
              {'x': 3, 'y': 0, 'z': 3}, {'x': 3, 'y': 0, 'z': 4}]
    target = {'shows': [{'boundingBox': bounds}]}
    sequence = InteractiveSequence(BODY_TEMPLATE, RetrievalGoal(),
                                   InteractivePlan('mock'))
    wall = sequence._create_interior_wall(
        'test_material',
        [],
        geometry.ORIGIN_LOCATION,
        [bounds],
        [target]
    )
    wall_poly = geometry.rect_to_poly(wall['shows'][0]['boundingBox'])
    assert not geometry.does_fully_obstruct_target(
        geometry.ORIGIN, target, wall_poly)


def test_choose_confusor_definition():
    goal = RetrievalGoal()
    target_definition = goal.choose_target_definition(0)
    assert target_definition

    sequence = InteractiveSequence(BODY_TEMPLATE, goal,
                                   InteractivePlan('mock'))
    definition = sequence._choose_confusor_definition(target_definition)
    assert definition

    is_same_color = set(definition['color']) == set(target_definition['color'])
    is_same_shape = definition['shape'] == target_definition['shape']
    is_same_size = definition['size'] == target_definition['size'] and (
        definition['dimensions']['x'] >=
        target_definition['dimensions']['x'] -
        util.MAX_SIZE_DIFFERENCE
    ) and (
        definition['dimensions']['x'] <=
        target_definition['dimensions']['x'] +
        util.MAX_SIZE_DIFFERENCE
    ) and (
        definition['dimensions']['y'] >=
        target_definition['dimensions']['y'] -
        util.MAX_SIZE_DIFFERENCE
    ) and (
        definition['dimensions']['y'] <=
        target_definition['dimensions']['y'] +
        util.MAX_SIZE_DIFFERENCE
    ) and (
        definition['dimensions']['z'] >=
        target_definition['dimensions']['z'] -
        util.MAX_SIZE_DIFFERENCE
    ) and (
        definition['dimensions']['z'] <=
        target_definition['dimensions']['z'] +
        util.MAX_SIZE_DIFFERENCE
    )
    assert (is_same_size and is_same_shape and not is_same_color) or \
        (is_same_size and is_same_color and not is_same_shape) or \
        (is_same_shape and is_same_color and not is_same_size)


def test_choose_distractor_definition():
    goal = RetrievalGoal()
    target_definition = goal.choose_definition()
    target_location, bounds_list = goal.choose_location(
        target_definition,
        geometry.ORIGIN_LOCATION,
        []
    )
    target = util.instantiate_object(target_definition, target_location)
    assert target

    sequence = InteractiveSequence(BODY_TEMPLATE, goal,
                                   InteractivePlan('mock'))
    definition = sequence._choose_distractor_definition([target])
    assert definition
    assert definition['shape'] != target['shape']


def test_choose_obstructor_definition():
    goal = RetrievalGoal()
    target_definition = goal.choose_definition()
    assert target_definition

    sequence = InteractiveSequence(BODY_TEMPLATE, goal,
                                   InteractivePlan('mock'))
    definition = sequence._choose_obstructor_definition(target_definition,
                                                        False)
    assert definition['obstruct'] == 'navigation'

    if definition['rotation']['y'] == 0:
        assert (
            definition['dimensions']['x'] >=
            target_definition['dimensions']['x'] -
            util.MAX_SIZE_DIFFERENCE)
    elif definition['rotation']['y'] == 90:
        assert (
            definition['dimensions']['z'] >=
            target_definition['dimensions']['z'] -
            util.MAX_SIZE_DIFFERENCE)
    else:
        assert False


def test_choose_obstructor_definition_obstruct_vision():
    goal = RetrievalGoal()
    target_definition = goal.choose_definition()
    assert target_definition

    sequence = InteractiveSequence(BODY_TEMPLATE, goal,
                                   InteractivePlan('mock'))
    definition = sequence._choose_obstructor_definition(target_definition,
                                                        True)
    assert definition['obstruct'] == 'vision'
    assert (
        definition['dimensions']['y'] >= target_definition['dimensions']['y'] -
        util.MAX_SIZE_DIFFERENCE)

    if definition['rotation']['y'] == 0:
        assert (
            definition['dimensions']['x'] >=
            target_definition['dimensions']['x'] -
            util.MAX_SIZE_DIFFERENCE)
    elif definition['rotation']['y'] == 90:
        assert (
            definition['dimensions']['z'] >=
            target_definition['dimensions']['z'] -
            util.MAX_SIZE_DIFFERENCE)
    else:
        assert False


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


def verify_goal_config(sequence):
    for i in [1, 2]:
        scene = sequence.get_scenes()[i - 1]

        assert scene['performerStart'] == sequence._performer_start
        assert scene['goal']['last_step'] == 600

        goal_template = sequence._goal.get_goal_template()
        assert scene['goal']['category'] == goal_template['category']
        assert scene['goal']['domain_list'] == goal_template['domain_list']
        assert scene['goal']['description']

        type_list = scene['goal']['type_list']
        for type in goal_template['type_list']:
            assert type in type_list

        prefix = 'pair scene ' + str(i)
        assert prefix in type_list
        assert sequence.get_name() in type_list

        assert (
            (prefix + ' target location in front of performer start')
            in type_list or
            (prefix + ' target location in back of performer start')
            in type_list or
            (prefix + ' target location random') in type_list
        )

        target_list = sequence._target_list_per_scene[i - 1]
        assert ('targets ' + str(len(target_list))) in type_list

        confusor_list = sequence._confusor_list_per_scene[i - 1]
        assert ('confusors ' + str(len(confusor_list))) in type_list

        distractor_list = sequence._distractor_list + \
            sequence._receptacle_list_per_scene[i - 1]
        assert ('distractors ' + str(len(distractor_list))) in type_list

        obstructor_list = sequence._obstructor_list_per_scene[i - 1]
        assert ('obstructors ' + str(len(obstructor_list))) in type_list

        wall_list = sequence._interior_wall_list
        assert ('walls ' + str(len(wall_list))) in type_list

        containerize = is_true(sequence._plan.target_containerize, i)
        assert (
            prefix + ' target ' + ('is' if containerize else 'isn\'t') +
            ' hidden inside receptacle'
        ) in type_list
        assert (
            'target ' + ('' if containerize else 'not ') + 'enclosed'
        ) in type_list

        if len(confusor_list) > 0:
            assert prefix + ' confusor does exist'
            containerize = is_true(sequence._plan.confusor_containerize, i)
            assert (
                prefix + ' confusor ' + ('is' if containerize else 'isn\'t') +
                ' hidden inside receptacle'
            ) in type_list
            assert (
                'confusor ' + ('' if containerize else 'not ') + 'enclosed'
            ) in type_list

            assert (
                (prefix + ' confusor location in front of performer start')
                in type_list or
                (prefix + ' confusor location in back of performer start')
                in type_list or
                (prefix + ' confusor location very close to target')
                in type_list or
                (prefix + ' confusor location far away from target')
                in type_list
            )
        else:
            assert prefix + ' confusor doesn\'t exist'

        if len(obstructor_list) > 0:
            assert prefix + ' obstructor does exist'
        else:
            assert prefix + ' obstructor doesn\'t exist'

        target_metadata = (
            scene['goal']['metadata']['target']
            if 'target' in scene['goal']['metadata']
            else scene['goal']['metadata']['target_1']
        )

        assert target_metadata['id'] == target_list[0]['id']
        assert target_metadata['info'] == target_list[0]['info']

        tag_to_objects = {
            'confusor': confusor_list,
            'distractor': distractor_list,
            'obstructor': obstructor_list,
            'target': target_list,
            'wall': wall_list
        }

        for tag, object_list in tag_to_objects.items():
            for item in object_list:
                for info in item['info']:
                    assert (tag + ' ' + info) in scene['goal']['info_list']


def verify_immediately_visible(
    performer_start,
    object_list,
    target,
    adjacent=None,
    name='target'
):
    target_or_parent = get_parent(target, object_list) \
        if 'locationParent' in target else target
    target_poly = geometry.get_bounding_polygon(target_or_parent)

    view_line = shapely.geometry.LineString([[0, 0], [0, MAX_DIMENSION]])
    view_line = affinity.rotate(
        view_line, -performer_start['rotation']['y'], origin=(0, 0)
    )
    view_line = affinity.translate(
        view_line,
        performer_start['position']['x'],
        performer_start['position']['z']
    )

    if not target_poly.intersection(view_line):
        print(f'[ERROR] {name.upper()} SHOULD BE VISIBLE IN FRONT OF '
              f'PERFORMER:\n{name}={target_or_parent}\n'
              f'performer_start={performer_start}')
        return False

    ignore_id_list = [target['id'], target_or_parent['id']]
    if adjacent:
        ignore_id_list.append(adjacent['id'])
        if 'locationParent' in adjacent:
            ignore_id_list.append(get_parent(adjacent)['id'])

    for object_instance in object_list:
        if (
            object_instance['id'] not in ignore_id_list and
            'locationParent' not in object_instance
        ):
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
    performer_start,
    object_list,
    target,
    adjacent=None,
    name='target'
):
    result = verify_immediately_visible(performer_start, object_list, target,
                                        adjacent, name)
    if result:
        target_or_parent = get_parent(
            target, object_list) if 'locationParent' in target else target
        print(f'[ERROR] {name.upper()} SHOULD NOT BE VISIBLE IN FRONT OF '
              f'PERFORMER:\n{name}={target_or_parent}\n'
              f'performer_start={performer_start}')
    return not result


def verify_obstructor(scene, obstructor, target, performer_start,
                      obstruct_vision=False):
    print(f'[DEBUG] obstructor={obstructor}')
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
        if (
            object_instance['id'] not in ignore_id_list and
            'locationParent' not in object_instance
        ):
            object_poly = geometry.get_bounding_polygon(object_instance)
            if geometry.does_fully_obstruct_target(
                performer_start['position'], target, object_poly
            ):
                print(
                    f'[ERROR] NON-OBSTRUCTOR SHOULD NOT OBSTRUCT TARGET:\n'
                    f'object={object_instance}\ntarget={target}\n'
                    f'performer_start={performer_start}')
                return False

    return True


def verify_same_object_list(name, list_1, list_2, ignore_id_list):
    modified_object_list_1 = [
        instance for instance in list_1 if instance['id'] not in ignore_id_list
    ]
    modified_object_list_2 = [
        instance for instance in list_2 if instance['id'] not in ignore_id_list
    ]
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


def verify_pair(sequence, target_same_position=True,
                confusor_same_position=True, target_parent_same_position=True,
                confusor_parent_same_position=True, target_parent_same=True,
                confusor_parent_same=True, target_confusor_adjacent=False):

    verify_goal_config(sequence)
    scene_1 = sequence.get_scenes()[0]
    scene_2 = sequence.get_scenes()[1]
    assert scene_1
    assert scene_2

    # Ensure the performer start in each scene is the same.
    if scene_1['performerStart'] != scene_2['performerStart']:
        print(
            f'[ERROR] performer_start SHOULD BE THE SAME: '
            f'{scene_1["performerStart"]} != {scene_2["performerStart"]}')
        return False

    performer_start_poly = geometry.rect_to_poly(
        geometry.find_performer_rect(sequence._performer_start['position'])
    )
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
    target_1 = sequence._target_list_per_scene[0][0]
    assert target_1
    print(f'[DEBUG] target_1={target_1}')
    target_2 = sequence._target_list_per_scene[1][0]
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
            (['isParentOf'] if target_confusor_adjacent else []) +
            ([] if target_parent_same_position else ['shows'])
        ):
            return False

    # If a scene has a confusor, verify that it's a confusor of the target.
    confusor_1 = sequence._confusor_list_per_scene[0][0] if len(
        sequence._confusor_list_per_scene[0]) > 0 else None
    print(f'[DEBUG] confusor_1={confusor_1}')
    if confusor_1 and not verify_confusor(target_1, confusor_1):
        return False
    confusor_2 = sequence._confusor_list_per_scene[1][0] if len(
        sequence._confusor_list_per_scene[1]) > 0 else None
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
            (['isParentOf'] if target_confusor_adjacent else []) +
            ([] if confusor_parent_same_position else ['shows'])
        ):
            return False

    obstructor_1 = sequence._obstructor_list_per_scene[0][0] if len(
        sequence._obstructor_list_per_scene[0]) > 0 else None
    obstructor_2 = sequence._obstructor_list_per_scene[1][0] if len(
        sequence._obstructor_list_per_scene[1]) > 0 else None

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
        confusor_parent_2['id'] if confusor_parent_2 else None,
        obstructor_1['id'] if obstructor_1 else None,
        obstructor_2['id'] if obstructor_2 else None
    ] if object_id]

    # Ensure the random distractors are the same across the scenes.
    if not verify_same_object_list(
        'objects',
        scene_1['objects'],
        scene_2['objects'],
        ignore_id_list
    ):
        return False

    return True


def test_Pair1():
    sequence_factory = InteractivePairFactory(1, RetrievalGoal())
    sequence = sequence_factory.build(BODY_TEMPLATE)
    scenes = sequence.get_scenes()

    containerize = (
        sequence._plan.target_containerize == BoolPlan.YES_YES
    )
    # The target's position is the same if it's in a box because only its box
    # will have a different position.
    assert verify_pair(sequence, target_same_position=containerize,
                       target_parent_same_position=False)

    target_1 = sequence._target_list_per_scene[0][0]
    target_2 = sequence._target_list_per_scene[1][0]
    if containerize:
        assert verify_immediately_visible(
            sequence._performer_start,
            scenes[0]['objects'],
            get_parent(target_1, scenes[0]['objects'])
        )
        assert verify_not_immediately_visible(
            sequence._performer_start,
            scenes[1]['objects'],
            get_parent(target_2, scenes[1]['objects'])
        )
    else:
        assert verify_immediately_visible(
            sequence._performer_start,
            scenes[0]['objects'],
            target_1)
        assert verify_not_immediately_visible(
            sequence._performer_start, scenes[1]['objects'], target_2)

    assert len(sequence._confusor_list_per_scene[0]) == 0
    assert len(sequence._confusor_list_per_scene[1]) == 0
    assert len(sequence._obstructor_list_per_scene[0]) == 0
    assert len(sequence._obstructor_list_per_scene[1]) == 0


def test_Pair2():
    sequence_factory = InteractivePairFactory(2, RetrievalGoal())
    sequence = sequence_factory.build(BODY_TEMPLATE)
    scenes = sequence.get_scenes()

    containerize = (
        sequence._plan.target_containerize == BoolPlan.YES_YES
    )
    assert verify_pair(sequence)

    assert len(sequence._confusor_list_per_scene[0]) == 0
    assert len(sequence._confusor_list_per_scene[1]) == 0
    assert len(sequence._obstructor_list_per_scene[0]) == 0
    assert len(sequence._obstructor_list_per_scene[1]) == 1

    target_1 = sequence._target_list_per_scene[0][0]
    target_2 = sequence._target_list_per_scene[1][0]
    assert verify_obstructor(scenes[1],
                             sequence._obstructor_list_per_scene[1][0],
                             target_2, sequence._performer_start,
                             obstruct_vision=True)

    if containerize:
        assert verify_immediately_visible(
            sequence._performer_start,
            scenes[0]['objects'],
            get_parent(target_1, scenes[0]['objects'])
        )
        assert verify_not_immediately_visible(
            sequence._performer_start,
            scenes[1]['objects'],
            get_parent(target_2, scenes[1]['objects'])
        )
    else:
        assert verify_immediately_visible(
            sequence._performer_start,
            scenes[0]['objects'],
            target_1)
        assert verify_not_immediately_visible(
            sequence._performer_start, scenes[1]['objects'], target_2)


def test_Pair3():
    sequence_factory = InteractivePairFactory(3, RetrievalGoal())
    sequence = sequence_factory.build(BODY_TEMPLATE)

    containerize = (
        sequence._plan.target_containerize == BoolPlan.YES_YES
    )
    # The target's position is NOT the same if it's in a box because of how
    # the confusor's positioned next to it.
    assert verify_pair(sequence, target_same_position=(not containerize),
                       target_confusor_adjacent=True)

    assert len(sequence._confusor_list_per_scene[0]) == 0
    assert len(sequence._confusor_list_per_scene[1]) == 1
    assert len(sequence._obstructor_list_per_scene[0]) == 0
    assert len(sequence._obstructor_list_per_scene[1]) == 0

    target_1 = sequence._target_list_per_scene[0][0]
    target_2 = sequence._target_list_per_scene[1][0]
    confusor_2 = sequence._confusor_list_per_scene[1][0]
    assert geometry.are_adjacent(target_2, confusor_2)
    if containerize:
        assert target_1['locationParent']
        assert target_2['locationParent'] == confusor_2['locationParent']
    else:
        assert 'locationParent' not in target_1
        assert 'locationParent' not in target_2
        assert 'locationParent' not in confusor_2


def test_Pair4():
    sequence_factory = InteractivePairFactory(4, RetrievalGoal())
    sequence = sequence_factory.build(BODY_TEMPLATE)
    scenes = sequence.get_scenes()

    containerize = (
        sequence._plan.target_containerize == BoolPlan.YES_YES
    )
    assert verify_pair(sequence)

    assert len(sequence._confusor_list_per_scene[0]) == 0
    assert len(sequence._confusor_list_per_scene[1]) == 1
    assert len(sequence._obstructor_list_per_scene[0]) == 0
    assert len(sequence._obstructor_list_per_scene[1]) == 0

    target_1 = sequence._target_list_per_scene[0][0]
    target_2 = sequence._target_list_per_scene[1][0]
    confusor_2 = sequence._confusor_list_per_scene[1][0]
    if containerize:
        assert target_1['locationParent']
        assert target_2['locationParent'] != confusor_2['locationParent']
        assert not geometry.are_adjacent(
            get_parent(target_2, scenes[1]['objects']),
            get_parent(confusor_2, scenes[1]['objects'])
        )
    else:
        assert 'locationParent' not in target_1
        assert 'locationParent' not in target_2
        assert 'locationParent' not in confusor_2
        assert not geometry.are_adjacent(target_2, confusor_2)


def test_Pair5():
    sequence_factory = InteractivePairFactory(5, RetrievalGoal())
    sequence = sequence_factory.build(BODY_TEMPLATE)
    scenes = sequence.get_scenes()

    containerize = (
        sequence._plan.target_containerize == BoolPlan.YES_YES
    )
    # The target's position is NOT the same if it's in a box because of how
    # the confusor's positioned next to it.
    assert verify_pair(sequence, target_same_position=(not containerize),
                       confusor_same_position=False,
                       confusor_parent_same=False,
                       target_confusor_adjacent=True)

    assert len(sequence._confusor_list_per_scene[0]) == 1
    assert len(sequence._confusor_list_per_scene[1]) == 1
    assert len(sequence._obstructor_list_per_scene[0]) == 0
    assert len(sequence._obstructor_list_per_scene[1]) == 0

    target_1 = sequence._target_list_per_scene[0][0]
    target_2 = sequence._target_list_per_scene[1][0]
    confusor_1 = sequence._confusor_list_per_scene[0][0]
    confusor_2 = sequence._confusor_list_per_scene[1][0]
    assert geometry.are_adjacent(target_1, confusor_1)
    if containerize:
        assert target_1['locationParent'] == confusor_1['locationParent']
        assert target_2['locationParent'] != confusor_2['locationParent']
        assert not geometry.are_adjacent(
            get_parent(target_2, scenes[1]['objects']),
            get_parent(confusor_2, scenes[1]['objects'])
        )
    else:
        assert 'locationParent' not in target_1
        assert 'locationParent' not in target_2
        assert 'locationParent' not in confusor_1
        assert 'locationParent' not in confusor_2
        assert not geometry.are_adjacent(target_2, confusor_2)


def test_Pair6():
    sequence_factory = InteractivePairFactory(6, RetrievalGoal())
    sequence = sequence_factory.build(BODY_TEMPLATE)
    scenes = sequence.get_scenes()

    containerize = (
        sequence._plan.target_containerize == BoolPlan.YES_YES
    )
    # The object's position is the same if it's in a box because only its box
    # will have a different position.
    assert verify_pair(sequence, target_same_position=containerize,
                       confusor_same_position=containerize,
                       target_parent_same_position=False,
                       confusor_parent_same_position=False)

    assert len(sequence._confusor_list_per_scene[0]) == 1
    assert len(sequence._confusor_list_per_scene[1]) == 1
    assert len(sequence._obstructor_list_per_scene[0]) == 0
    assert len(sequence._obstructor_list_per_scene[1]) == 0

    target_1 = sequence._target_list_per_scene[0][0]
    target_2 = sequence._target_list_per_scene[1][0]
    confusor_1 = sequence._confusor_list_per_scene[0][0]
    confusor_2 = sequence._confusor_list_per_scene[1][0]
    if containerize:
        assert target_1['locationParent'] != confusor_1['locationParent']
        assert target_2['locationParent'] != confusor_2['locationParent']
        assert verify_immediately_visible(
            sequence._performer_start,
            scenes[0]['objects'],
            get_parent(target_1, scenes[0]['objects'])
        )
        assert verify_not_immediately_visible(
            sequence._performer_start,
            scenes[1]['objects'],
            get_parent(target_2, scenes[1]['objects'])
        )
        assert verify_not_immediately_visible(
            sequence._performer_start,
            scenes[0]['objects'],
            get_parent(confusor_1, scenes[0]['objects']),
            name='confusor'
        )
        assert verify_immediately_visible(
            sequence._performer_start,
            scenes[1]['objects'],
            get_parent(confusor_2, scenes[1]['objects']),
            name='confusor'
        )
    else:
        assert 'locationParent' not in target_1
        assert 'locationParent' not in target_2
        assert 'locationParent' not in confusor_1
        assert 'locationParent' not in confusor_2
        assert verify_immediately_visible(
            sequence._performer_start,
            scenes[0]['objects'],
            target_1)
        assert verify_not_immediately_visible(
            sequence._performer_start, scenes[1]['objects'], target_2)
        assert verify_not_immediately_visible(
            sequence._performer_start,
            scenes[0]['objects'],
            confusor_1,
            name='confusor'
        )
        assert verify_immediately_visible(
            sequence._performer_start,
            scenes[1]['objects'],
            confusor_2,
            name='confusor'
        )


def test_Pair7():
    sequence_factory = InteractivePairFactory(7, RetrievalGoal())
    sequence = sequence_factory.build(BODY_TEMPLATE)
    scenes = sequence.get_scenes()

    # The target's position is the same if it's in a box because only its box
    # will have a different position.
    assert verify_pair(sequence, confusor_same_position=False,
                       target_parent_same_position=False)

    assert len(sequence._confusor_list_per_scene[0]) == 1
    assert len(sequence._confusor_list_per_scene[1]) == 1
    assert len(sequence._obstructor_list_per_scene[0]) == 0
    assert len(sequence._obstructor_list_per_scene[1]) == 0

    target_1 = sequence._target_list_per_scene[0][0]
    target_2 = sequence._target_list_per_scene[1][0]
    confusor_1 = sequence._confusor_list_per_scene[0][0]
    confusor_2 = sequence._confusor_list_per_scene[1][0]
    assert verify_not_immediately_visible(
        sequence._performer_start,
        scenes[0]['objects'],
        confusor_1,
        name='confusor'
    )
    assert verify_immediately_visible(
        sequence._performer_start,
        scenes[1]['objects'],
        confusor_2,
        name='confusor')
    assert 'locationParent' in target_1
    assert 'locationParent' in target_2
    assert 'locationParent' not in confusor_1
    assert 'locationParent' not in confusor_2
    assert verify_immediately_visible(
        sequence._performer_start,
        scenes[0]['objects'],
        get_parent(target_1, scenes[0]['objects'])
    )
    assert verify_not_immediately_visible(
        sequence._performer_start,
        scenes[1]['objects'],
        get_parent(target_2, scenes[1]['objects'])
    )


def test_Pair8():
    sequence_factory = InteractivePairFactory(8, RetrievalGoal())
    sequence = sequence_factory.build(BODY_TEMPLATE)
    scenes = sequence.get_scenes()

    assert verify_pair(sequence, target_same_position=False,
                       target_parent_same=False)

    assert len(sequence._confusor_list_per_scene[0]) == 1
    assert len(sequence._confusor_list_per_scene[1]) == 1
    assert len(sequence._obstructor_list_per_scene[0]) == 0
    assert len(sequence._obstructor_list_per_scene[1]) == 0

    target_1 = sequence._target_list_per_scene[0][0]
    target_2 = sequence._target_list_per_scene[1][0]
    confusor_1 = sequence._confusor_list_per_scene[0][0]
    confusor_2 = sequence._confusor_list_per_scene[1][0]
    assert geometry.are_adjacent(target_1, confusor_1)
    assert geometry.are_adjacent(
        get_parent(
            target_2,
            scenes[1]['objects']),
        confusor_2)
    assert 'locationParent' not in target_1
    assert 'locationParent' in target_2
    assert 'locationParent' not in confusor_1
    assert 'locationParent' not in confusor_2


def test_Pair9():
    sequence_factory = InteractivePairFactory(9, RetrievalGoal())
    sequence = sequence_factory.build(BODY_TEMPLATE)
    scenes = sequence.get_scenes()

    containerize = (
        sequence._plan.target_containerize == BoolPlan.YES_YES
    )
    assert verify_pair(sequence)

    assert len(sequence._confusor_list_per_scene[0]) == 0
    assert len(sequence._confusor_list_per_scene[1]) == 0
    assert len(sequence._obstructor_list_per_scene[0]) == 0
    assert len(sequence._obstructor_list_per_scene[1]) == 1

    target_1 = sequence._target_list_per_scene[0][0]
    target_2 = sequence._target_list_per_scene[1][0]
    assert verify_obstructor(scenes[1],
                             sequence._obstructor_list_per_scene[1][0],
                             target_2, sequence._performer_start,
                             obstruct_vision=False)

    if containerize:
        assert verify_immediately_visible(
            sequence._performer_start,
            scenes[0]['objects'],
            get_parent(target_1, scenes[0]['objects'])
        )
        assert verify_not_immediately_visible(
            sequence._performer_start,
            scenes[1]['objects'],
            get_parent(target_2, scenes[1]['objects'])
        )
    else:
        assert verify_immediately_visible(
            sequence._performer_start,
            scenes[0]['objects'],
            target_1)
        assert verify_not_immediately_visible(
            sequence._performer_start, scenes[1]['objects'], target_2)


def test_Pair11():
    sequence_factory = InteractivePairFactory(11, RetrievalGoal())
    sequence = sequence_factory.build(BODY_TEMPLATE)
    scenes = sequence.get_scenes()

    assert verify_pair(sequence, target_same_position=False,
                       confusor_same_position=False)

    target_1 = sequence._target_list_per_scene[0][0]
    target_2 = sequence._target_list_per_scene[1][0]
    confusor_1 = sequence._confusor_list_per_scene[0][0]
    confusor_2 = sequence._confusor_list_per_scene[1][0]
    assert verify_immediately_visible(
        sequence._performer_start,
        scenes[0]['objects'],
        target_1,
        confusor_1)
    assert verify_not_immediately_visible(
        sequence._performer_start,
        scenes[1]['objects'],
        target_2,
        confusor_2)
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
    # Same InteractivePlan as Pair2
    plan = InteractivePlan(
        'pair 2',
        target_definition=sofa,
        target_location=TargetLocationPlan.FRONT_FRONT,
        obstructor=ObstructorPlan.NONE_VISION,
        obstructor_definition=copy.deepcopy(sofa)
    )
    sequence = InteractiveSequence(BODY_TEMPLATE, TraversalGoal(), plan)
    scenes = sequence.get_scenes()
    assert verify_pair(sequence)

    assert len(sequence._confusor_list_per_scene[0]) == 0
    assert len(sequence._confusor_list_per_scene[1]) == 0
    assert len(sequence._obstructor_list_per_scene[0]) == 0
    assert len(sequence._obstructor_list_per_scene[1]) == 1

    target_1 = sequence._target_list_per_scene[0][0]
    target_2 = sequence._target_list_per_scene[1][0]
    assert verify_obstructor(scenes[1],
                             sequence._obstructor_list_per_scene[1][0],
                             target_2, sequence._performer_start,
                             obstruct_vision=True)

    assert verify_immediately_visible(
        sequence._performer_start,
        scenes[0]['objects'],
        target_1)
    assert verify_not_immediately_visible(
        sequence._performer_start,
        scenes[1]['objects'],
        target_2)
