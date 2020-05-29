import uuid
from typing import Tuple, Dict, Any

import geometry
from goals import *
from goal import generate_wall, MIN_WALL_WIDTH, MAX_WALL_WIDTH, WALL_HEIGHT, WALL_DEPTH, MAX_OBJECTS
from util import instantiate_object


def test_generate_wall():
    material = 'wall material'
    wall = generate_wall(material, geometry.ORIGIN, [])
    assert wall['id'].startswith('wall_')
    assert wall['materials'] == [material]
    shows = wall['shows'][0]
    assert shows['stepBegin'] == 0
    assert MIN_WALL_WIDTH <= shows['scale']['x'] <= MAX_WALL_WIDTH
    assert shows['scale']['y'] == WALL_HEIGHT
    assert shows['scale']['z'] == WALL_DEPTH
    assert shows['rotation']['x'] == 0
    assert shows['rotation']['z'] == 0


class DummyGoal(Goal):
    """Implements just enough to test some Goal methods"""
    def __init__(self):
        super(DummyGoal, self).__init__()

    def find_optimal_path(self, goal_objects: List[Dict[str, Any]], all_objects: List[Dict[str, Any]]) -> \
            List[Dict[str, Any]]:
        return []

    def compute_objects(self, wall_material_name: str) -> \
            Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[List[Dict[str, float]]]]:
        return [], [], []


def test_Goal_update_body():
    goal_obj = DummyGoal()
    body = {
        'wallMaterial': 'dummy wall material'
    }
    goal_obj.update_body(body, False)
    assert 'performerStart' in body
    assert 'objects' in body
    assert 'goal' in body


def test_Goal_compute_performer_start():
    goal_obj = DummyGoal()
    start = goal_obj.compute_performer_start()
    position = start['position']
    assert 'x' in position
    assert 'z' in position
    assert position['y'] == 0
    assert 'y' in start['rotation']


def test_Goal_choose_object_def():
    goal_obj = DummyGoal()
    obj_def = goal_obj.choose_object_def()
    assert obj_def is not None
    assert 'choose' not in obj_def


def test_Goal_add_objects():
    goal_obj = DummyGoal()
    obj_list = []
    rect_list = []
    performer_position = geometry.ORIGIN
    goal_obj.add_objects(obj_list, rect_list, performer_position)
    num_objs = len(obj_list)
    assert len(rect_list) == num_objs
    assert 1 <= num_objs <= MAX_OBJECTS


def test_Goal__update_goal_info_list():
    goal_obj = DummyGoal()
    goal = { 'info_list': [ 'thing1' ] }
    objs = [{
        'info': ['thing1', 'thing2']
    },
    {
        'info': ['thing2', 'thing3']
    }]
    expected_info = {'thing1', 'thing2', 'thing3'}
    goal_obj._update_goal_info_list(goal, objs)
    info = set(goal['info_list'])
    assert info == expected_info

    
def test_Goal_duplicate_object():
    goal_obj = RetrievalGoal()
    obj = {
        'id': str(uuid.uuid4()),
        'info': [str(uuid.uuid4())],
        'type': 'sphere',
        "choose": [{
            "mass": 0.25,
            "materialCategory": ["plastic"],
            "salientMaterials": ["plastic", "hollow"]
        }, {
            "mass": 0.5625,
            "materialCategory": ["rubber"],
            "salientMaterials": ["rubber"]
        }, {
            "mass": 0.5625,
            "materialCategory": ["block_blank"],
            "salientMaterials": ["wood"]
        }, {
            "mass": 0.5625,
            "materialCategory": ["wood"],
            "salientMaterials": ["wood"]
        }, {
            "mass": 1,
            "materialCategory": ["metal"],
            "salientMaterials": ["metal"]
        }],
        "attributes": ["moveable", "pickupable"],
        "dimensions": {
            "x": 0.1,
            "y": 0.1,
            "z": 0.1
        },
        "position_y": 0.05,
        "scale": {
            "x": 0.1,
            "y": 0.1,
            "z": 0.1
        }
    }
    object_location = {
        'position': {
            'x': 0.0,
            'y': 0.0,
            'z': 0.0
        },
        'rotation': {
            'x': 0.0,
            'y': 0.0,
            'z': 0.0
        }
    }
    sphere = instantiate_object(obj, object_location)
    object_list = [sphere]
    bounding_rect = [[{'x': 3.7346446609406727, 'y': 0, 'z': 4.23}, {'x': 3.77, 'y': 0, 'z': 4.265355339059328}, {'x': 3.8053553390593273, 'y': 0, 'z': 4.23}, {'x': 3.77, 'y': 0, 'z': 4.194644660940673}], [{'x': 3.846, 'y': 0, 'z': -1.9685000000000001}, {'x': 3.846, 'y': 0, 'z': -2.4715000000000003}, {'x': 3.1340000000000003, 'y': 0, 'z': -2.4715000000000003}, {'x': 3.1340000000000003, 'y': 0, 'z': -1.9685000000000001}]]
    performer_position = {'x': 0.77, 'y': 0, 'z': -0.41}
    goal = goal_obj.get_config(object_list, object_list)
    goal_obj.add_objects(object_list, bounding_rect, performer_position)



