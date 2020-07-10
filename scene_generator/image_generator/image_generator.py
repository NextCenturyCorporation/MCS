#!/usr/bin/env python3

import itertools
import json
import numpy
import os
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

def generate_output_file_name(object_type, material_list):
    material_name_list = [item[(item.rfind('/') + 1):].lower().replace(' ', '_') for item in material_list]
    return object_type + ('_' if len(material_name_list) > 0 else '') + ('_'.join(material_name_list))

def generate_scene_configuration(object_definition, material_list): 
    scene_configuration = {
        'name': 'screenshot',
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
    return scene_configuration_list

def get_global_material_list(material):
    return getattr(materials, material.upper() + '_MATERIALS')

def retrieve_image_pixel_list(object_screenshot):
    # Retrieve a two-dimensional list of pixel tuples from the Pillow Image
    pixels = list(object_screenshot.getdata())
    width, height = object_screenshot.size
    return [pixels[i * width:(i + 1) * width] for i in range(0, height)]

def main(args):
    if len(args) < 2:
        print('Usage: python image_generator.py <unity_app_file_path> <output_folder=../images/>')
        exit()

    controller = MCS.create_controller(args[1])

    scene_configuration_list = generate_scene_configuration_list(simplified_objects.OBJECT_LIST)

    output_folder = (args[2] if len(args) > 2 else '../images') + '/'

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for scene_configuration in scene_configuration_list:
        object_config = scene_configuration['objects'][0]
        object_type = object_config['type']
        material_list = object_config['materials'] if 'materials' in object_config else []

        print('type = ' + object_type + ', materials = ' + json.dumps(material_list))

        step_output = controller.start_scene(scene_configuration)
        object_screenshot = step_output.image_list[0]

        # Shrink and crop the object's screenshot to reduce its size.
        object_screenshot = object_screenshot.resize((300, 200))
        object_screenshot = object_screenshot.crop(ImageOps.invert(object_screenshot).getbbox())

        output_file_name = output_folder + generate_output_file_name(object_type, material_list)
        object_screenshot.save(fp=output_file_name + '.png')

        pixels = retrieve_image_pixel_list(object_screenshot)

        with open(output_file_name + '.txt', 'w') as output_text_file:
            output_text_file.write(json.dumps(PrettyJsonNoIndent(pixels), cls=PrettyJsonEncoder))

if __name__ == '__main__':
    main(sys.argv)

