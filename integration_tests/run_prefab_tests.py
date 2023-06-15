import argparse
import copy
import json
import time
import urllib.request

from integration_test_utils import (DEFAULT_TEST_CONFIGS, add_test_args,
                                    print_divider)

import machine_common_sense as mcs
from machine_common_sense.logging_config import LoggingConfig

# Template for test scenes.
SCENE_TEMPLATE = {
    'name': None,
    'version': 2,
    'ceilingMaterial': 'AI2-THOR/Materials/Walls/Drywall',
    'floorMaterial': 'AI2-THOR/Materials/Fabrics/CarpetWhite 3',
    'wallMaterial': 'AI2-THOR/Materials/Walls/Drywall',
    'performerStart': {
        'position': {
            'x': 0,
            'z': -4
        },
        'rotation': {
            'x': 0,
            'y': 0
        }
    },
    'objects': [{
        'id': None,
        'type': None,
        'kinematic': True,
        'physics': True,
        'materials': ['Custom/Materials/Blue'],
        'shows': [{
            'stepBegin': 0,
            'position': {
                'x': 0,
                'y': 0,
                'z': 1
            },
            'rotation': {
                'x': 0,
                'y': 45,
                'z': 0
            },
            'scale': {
                'x': 1,
                'y': 1,
                'z': 1
            }
        }]
    }]
}

# List of object registries.
OBJECT_REGISTRY_LIST = [
    'ai2thor_object_registry.json',
    'mcs_object_registry.json',
    'primitive_object_registry.json'
]

# URL for object registries (replacing branch_name and registry_name).
OBJECT_REGISTRY_URL = "https://raw.githubusercontent.com/NextCenturyCorporation/ai2thor/branch_name/unity/Assets/Addressables/MCS/registry_name"  # noqa: E501

# Materials for objects with material restrictions. It doesn't matter what the
# exact material is, as long as each object has a valid material configured.
MATERIALS = {
    'no_material': [],
    'flat_colors': ['Custom/Materials/Blue'],
    'armchair_thorkea': ['AI2-THOR/Objects/Physics/SimObjsPhysics/THORKEA Objects/THORKEA_Assets_Furniture/Armchair/Materials/THORKEA_Armchair_Ekemas_Fabric_Mat'],  # noqa: E501
    'block_blank': ['UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/blue_1x1'],  # noqa: E501
    'block_design': ['UnityAssetStore/KD_AlphabetBlocks/Assets/Textures/Blue/TOYBlocks_AlphabetBlock_A_Blue_1K/ToyBlockBlueA'],  # noqa: E501
    'cardboard': ['AI2-THOR/Materials/Misc/Cardboard_Brown'],
    'ceramic': ['AI2-THOR/Materials/Ceramics/GREYGRANITE'],
    'fabric': ['AI2-THOR/Materials/Fabrics/Carpet4'],
    'leather': ['AI2-THOR/Materials/Fabrics/Leather'],
    'leather_armchair': ['UnityAssetStore/Leather_Chair/Assets/Materials/Leather_Chair_NEW_1'],  # noqa: E501
    'metal': ['AI2-THOR/Materials/Metals/BrushedAluminum_Blue'],
    'plastic': ['AI2-THOR/Materials/Plastics/OrangePlastic'],
    'rubber': ['AI2-THOR/Materials/Plastics/LightBlueRubber'],
    'sofa_1': ['AI2-THOR/Materials/Fabrics/Sofa1_Blue'],
    'sofa_chair_1': ['AI2-THOR/Materials/Fabrics/SofaChair1_Salmon'],
    'sofa_2': ['AI2-THOR/Materials/Fabrics/Sofa2_Grey'],
    'sofa_3': ['AI2-THOR/Materials/Fabrics/Sofa3_Blue'],
    'sofa_8': ['Assets/Addressables/MCS/UnityAssetStore/Furniture/Source/Materials/3Seat_BaseColor'],  # noqa: E501
    'sofa_chair_8': ['Assets/Addressables/MCS/UnityAssetStore/Furniture/Source/Materials/fotel2_BaseColor'],  # noqa: E501
    'sofa_9': ['Assets/Addressables/MCS/UnityAssetStore/Furniture/Source/Materials/2Seat_BaseColor'],  # noqa: E501
    'sofa_thorkea': ['AI2-THOR/Objects/Physics/SimObjsPhysics/THORKEA Objects/THORKEA_Assets_Furniture/Sofa/Materials/THORKEA_Sofa_Alrid_Fabric_Mat'],  # noqa: E501
    'tools': ['UnityAssetStore/YughuesFreeMetalMaterials/Materials/M_YFMM_15'],
    'wall': ['AI2-THOR/Materials/Walls/EggshellDrywall'],
    'wood': ['AI2-THOR/Materials/Wood/WornWood']
}


def retrieve_registry_data(registry_name: str, branch_name: str) -> dict:
    # Retrieve the object registry data from the latest on GitHub.
    url = OBJECT_REGISTRY_URL
    url = url.replace("registry_name", registry_name)
    url = url.replace("branch_name", branch_name)
    with urllib.request.urlopen(url) as page:
        html = page.read().decode('utf-8')
        html = html.replace("\n", "").replace(" ", "")
        data = json.loads(html)
        return data['objects']
    return []


def start_prefab_tests(mcs_unity_version: str, branch_name: str) -> None:
    # Set logging.
    mcs.init_logging(LoggingConfig.get_errors_only_console_config())

    # Use the oracle MCS config file.
    config_file = DEFAULT_TEST_CONFIGS['oracle']

    # Create the controller and start Unity.
    controller = mcs.create_controller(
        unity_app_file_path=None,
        unity_cache_version=mcs_unity_version,
        config_file_or_dict=config_file
    )

    failed_scenes = []
    successful_scenes = []

    # Loop over each object registry file...
    for registry_name in OBJECT_REGISTRY_LIST:
        # Retrieve all of the objects in this registry.
        objects = retrieve_registry_data(registry_name, branch_name)
        print_divider()
        print(f'Reading {len(objects)} objects from {registry_name}')

        # Loop over each object...
        for entry in objects:
            object_type = entry['id']
            # Skip over deprecated objects.
            if (
                object_type == 'cake' or
                object_type.startswith('emoji_') or
                object_type.startswith('painting_') or
                object_type.startswith('plant_') or
                object_type.endswith('_faceless')
            ):
                continue

            # Generate the test scene to validate this object.
            scene_data = copy.deepcopy(SCENE_TEMPLATE)
            scene_data['name'] = f'prefab_test_{object_type}'
            scene_data['objects'][0]['id'] = f'test_{object_type}'
            scene_data['objects'][0]['type'] = object_type

            # Update the object's material if the object has any restrictions.
            material_restrictions = entry.get('materialRestrictions', [])
            if material_restrictions:
                materials = MATERIALS[material_restrictions[0]]
                scene_data['objects'][0]['materials'] = materials

            # Start the test scene, and wait for it to load.
            step_metadata = controller.start_scene(scene_data)
            time.sleep(1)

            # Ensure the object exists, is visible, and has texture/shape.
            successful = False
            if len(step_metadata.object_list) == 0:
                failed_scenes.append((
                    object_type,
                    ['No objects']
                ))
            else:
                object_metadata = step_metadata.object_list[0]
                failed_conditions = []
                if not object_metadata.visible:
                    failed_conditions.append('Not visible')
                if not object_metadata.texture_color_list:
                    failed_conditions.append('No texture color list')
                if not object_metadata.shape:
                    failed_conditions.append('No shape')
                if not object_metadata.position:
                    failed_conditions.append('No position')
                if not object_metadata.mass:
                    failed_conditions.append('No mass')
                if failed_conditions:
                    failed_scenes.append((
                        object_type,
                        failed_conditions
                    ))
                else:
                    successful_scenes.append(object_type)
                    successful = True

            # Record success or failure.
            if successful:
                print(f'{object_type} successful')
            else:
                conditions = failed_scenes[-1][1]
                print(f'{object_type} FAILED: {"; ".join(conditions)}')

            # End the current scene.
            controller.end_scene()

    # List each failed scene (if any).
    print_divider()
    print(
        f'Final results: {len(successful_scenes)} successful, '
        f'{len(failed_scenes)} failed'
    )
    if len(failed_scenes):
        print('Failed scenes:')
    for object_type, conditions in failed_scenes:
        print(f'    {object_type}: {"; ".join(conditions)}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run Prefab Integration Tests"
    )
    parser = add_test_args(parser)
    args = parser.parse_args()
    start_prefab_tests(
        args.mcs_unity_version,
        'development' if args.mcs_unity_version in ['dev', 'development']
        else 'master'
    )
