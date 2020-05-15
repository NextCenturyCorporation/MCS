import uuid

from goals import *
from util import instantiate_object


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



