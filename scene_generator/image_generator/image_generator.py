#!/usr/bin/env python3

import itertools
import json
import numpy
import sys

from machine_common_sense.mcs import MCS
from PIL import Image, ImageOps

import materials
import simplified_objects

sys.path.insert(1, '../pretty_json')
from pretty_json import PrettyJsonEncoder, PrettyJsonNoIndent

def generate_materials_lists(materials_options):
    materials_lists = []
    for material_category in materials_options:
        materials_lists_specific_category = []
        for material in material_category:
            material_list = [item[0] for item in get_global_material_list(material)]
            materials_lists_specific_category.append(material_list)
        if (len(materials_lists_specific_category) > 1):
            cross_product = list(itertools.product(*materials_lists_specific_category))
            materials_lists_specific_category = [list(item) for item in cross_product]
        else:
            materials_lists_specific_category = [[item] for item in materials_lists_specific_category[0]]
        materials_lists = materials_lists + materials_lists_specific_category
    return materials_lists

def generate_scene_configuration(object_definition, material_list): 
    scene_configuration = {
        'screenshot': True,
        'objects': [{
            'id': 'test_' + object_definition['type'],
            'type': object_definition['type'],
            'kinematic': True,
            'shows': [{
                'stepBegin': 0,
                'position': object_definition['position'],
                'scale': object_definition['scale']
            }]
        }]
    }
    if 'rotation' in object_definition:
        scene_configuration['objects'][0]['shows'][0]['rotation'] = object_definition['rotation']
    if material_list is not None:
        scene_configuration['objects'][0]['materials'] = material_list
    return scene_configuration

def generate_scene_configuration_list(object_list):
    scene_configuration_list = []
    for object_definition in object_list:
        materials_lists = generate_materials_lists(object_definition['materials_options']) if 'materials_options' \
            in object_definition else [None]
        for material_list in materials_lists:
            scene_configuration_data = generate_scene_configuration(object_definition, material_list)
            scene_configuration_list.append(scene_configuration_data)
            #save_json_file(object_definition['type'], 
    return scene_configuration_list

def get_global_material_list(material):
    return getattr(materials, material.upper() + '_MATERIALS')

def save_json_file(object_type, material_list, json_data): 
    material_string_list = [item[(item.rfind('/') + 1):].lower() for item in material_list]
    with open(object_type + '_' + ('_'.join(material_string_list)) + '.json', 'w') as json_file:
        json.dump(json_data, json_file, indent=4)

def stow_image_pixel_list(output_data, scene_configuration, object_screenshot):
    object_config = scene_configuration['objects'][0]
    object_type = object_config['type']
    material_list = object_config['materials'] if 'materials' in object_config else []

    print('type = ' + object_type + ', materials = ' + json.dumps(material_list))

    material_name_list = [item[(item.rfind('/') + 1):].lower().replace(' ', '_') for item in material_list]
    screenshot_name = object_type + ('_' if len(material_name_list) > 0 else '') + ('_'.join(material_name_list))
    object_screenshot.save(fp=screenshot_name + '.png')

    if object_type not in output_data:
        output_data[object_type] = {}

    output_nested = output_data[object_type]

    # Retrieve a two-dimensional list of pixel tuples from the Pillow Image
    pixels = list(object_screenshot.getdata())
    width, height = object_screenshot.size
    pixels = [pixels[i * width:(i + 1) * width] for i in range(0, height)]

    if len(material_list) == 0:
        output_data[object_type] = pixels
    else:
        for i in range(0, len(material_list)):
            if material_list[i] not in output_nested:
                output_nested[material_list[i]] = {}
            if i == len(material_list) - 1:
                output_nested[material_list[i]] = pixels
            output_nested = output_nested[material_list[i]]

    return output_data

def save_output_data(output_data):
    pretty_output_data = wrap_with_noindent(output_data)

    with open('images.py', 'w') as output_file:
        output_file.write('OBJECT_IMAGES = ' + json.dumps(pretty_output_data, cls=PrettyJsonEncoder, sort_keys=True, \
                indent=2))

def wrap_with_noindent(nested_data):
    for prop in nested_data:
        if isinstance(nested_data[prop], list):
            nested_data[prop] = PrettyJsonNoIndent(nested_data[prop])
        elif isinstance(nested_data[prop], dict):
            nested_data[prop] = wrap_with_noindent(nested_data[prop])
    return nested_data

def main(args):
    if len(args) < 2:
        print('Usage: python image_generator.py <unity_app_file_path>')
        exit()

    controller = MCS.create_controller(args[1])

    output_data = {}

    scene_configuration_list = generate_scene_configuration_list(simplified_objects.OBJECT_LIST)

    for scene_configuration in scene_configuration_list:
        step_output = controller.start_scene(scene_configuration)
        object_screenshot = step_output.image_list[0]

        object_screenshot = object_screenshot.resize((300, 200))
        object_screenshot = object_screenshot.crop(ImageOps.invert(object_screenshot).getbbox())

        output_data = stow_image_pixel_list(output_data, scene_configuration, object_screenshot)

    save_output_data(output_data)

if __name__ == '__main__':
    main(sys.argv)

