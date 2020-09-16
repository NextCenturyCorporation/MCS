from occluders import calculate_separation_distance, create_occluder, \
    generate_occluder_position
import pytest
import random


def test_create_occluder_normal():
    wall_material = ['test_material_wall', ['white']]
    pole_material = ['test_material_pole', ['brown']]
    x_position = random.uniform(-1, 1)
    x_scale = random.uniform(0.1, 2)

    occluder = create_occluder(
        wall_material,
        pole_material,
        x_position,
        x_scale)
    assert len(occluder) == 2
    wall, pole = occluder
    # make sure we got them back in the right order
    assert wall['type'] == 'cube'
    assert pole['type'] == 'cylinder'
    assert wall['materials'] == ['test_material_wall']
    assert pole['materials'] == ['test_material_pole']
    assert wall['info'] == ['white']
    assert pole['info'] == ['brown']
    for x in wall, pole:
        assert x['shows'][0]['position']['x'] == x_position


def test_create_occluder_sideways():
    wall_material = ['test_material_wall', ['white']]
    pole_material = ['test_material_pole', ['brown']]
    x_position = random.uniform(-1, 1)
    x_scale = random.uniform(0.1, 2)

    occluder = create_occluder(
        wall_material,
        pole_material,
        x_position,
        x_scale,
        True)
    assert len(occluder) == 2
    wall, pole = occluder
    # make sure we got them back in the right order
    assert wall['type'] == 'cube'
    assert pole['type'] == 'cylinder'
    assert wall['materials'] == ['test_material_wall']
    assert pole['materials'] == ['test_material_pole']
    assert wall['info'] == ['white']
    assert pole['info'] == ['brown']


def test_calculate_separation_distance():
    assert calculate_separation_distance(0.5, 1, 2.5, 1) == pytest.approx(0.5)
    assert calculate_separation_distance(0, 1, 2.5, 1) == pytest.approx(1)
    assert calculate_separation_distance(-1, 1, -3, 1) == pytest.approx(0.5)
    assert calculate_separation_distance(-1, 1, 2, 1) == pytest.approx(1.5)
    assert calculate_separation_distance(1, 0.5, 3, 0.5) == pytest.approx(1)
    assert calculate_separation_distance(1, 1, 2.5, 1) == pytest.approx(0)
    assert calculate_separation_distance(1, 1, 2, 1) == pytest.approx(-0.5)
    assert calculate_separation_distance(1, 1, 2, 2) == pytest.approx(-1)


def test_generate_occluder_position():
    assert -2.75 <= generate_occluder_position(0.5, []) <= 2.75
    assert -2.5 <= generate_occluder_position(1, []) <= 2.5

    occluder_1 = {'shows': [{'position': {'x': 2}, 'scale': {'x': 1}}]}
    assert -2.5 <= generate_occluder_position(1, [occluder_1]) <= 1

    occluder_2 = {'shows': [{'position': {'x': -2.25}, 'scale': {'x': 0.5}}]}
    assert -1.5 <= generate_occluder_position(1, [occluder_1, occluder_2]) <= 1
