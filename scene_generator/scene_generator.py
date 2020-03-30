#!/usr/bin/env python3
#

import sys
import argparse
import os
import os.path
import json
import copy
import random
import uuid
import math


from materials import *
from separating_axis_theorem import *


OUTPUT_TEMPLATE_JSON = """
{
  "name": "",
  "ceilingMaterial": "AI2-THOR/Materials/Walls/Drywall",
  "floorMaterial": "AI2-THOR/Materials/Fabrics/CarpetWhite 3",
  "wallMaterial": "AI2-THOR/Materials/Walls/DrywallBeige",
  "performerStart": {
    "position": {
      "x": 0,
      "z": 0
    },
    "rotation": {
      "y": 0
    }
  },
  "objects": [],
  "goal": {},
  "answer": {}
}
"""

OUTPUT_TEMPLATE = json.loads(OUTPUT_TEMPLATE_JSON)

# the following mins and maxes are inclusive
MIN_PERFORMER_POSITION = -4.8
MAX_PERFORMER_POSITION = 4.8
MIN_SCENE_POSITION = -4.95
MAX_SCENE_POSITION = 4.95
POSITION_DIGITS = 1
MIN_ROTATION = 0
MAX_ROTATION = 359
ROTATION_DIGITS = 0
MAX_TRIES = 6
MAX_OBJECTS = 5

def random_position():
    return round(random.uniform(MIN_PERFORMER_POSITION, MAX_PERFORMER_POSITION), POSITION_DIGITS)

def random_rotation():
    rotation = round(random.uniform(MIN_ROTATION, MAX_ROTATION), ROTATION_DIGITS)
    if ROTATION_DIGITS == 0:
        rotation = int(rotation)
    return rotation

def load_object_file(object_file_name):
    with open(object_file_name) as object_file:
        objects = json.load(object_file)
    return objects    
        
def dot_prod_dict(v1, v2):
    return sum (v1[key]*v2.get(key,0) for key in v1)

       
    
def collision(test_rect, test_point):
    #assuming test_rect is an array4 points in order... Clockwise or CCW does not matter
    #points are {x,y,z}
    #
    # From https://math.stackexchange.com/a/190373
    A=test_rect[0]
    B=test_rect[1]
    C=test_rect[2]
    
    vectorAB={'x': B['x']-A['x'], 'y': B['y']-A['y'], 'z': B['z']-A['z']}
    vectorBC={'x': C['x']-B['x'], 'y': C['y']-B['y'], 'z': C['z']-B['z']}
    
    vectorAM={'x': test_point['x']-A['x'], 'y': test_point['y']-A['y'], 'z': test_point['z']-A['z']}
    vectorBM={'x': test_point['x']-B['x'], 'y': test_point['y']-B['y'], 'z': test_point['z']-B['z']}
    
    return (0<=dot_prod_dict(vectorAB, vectorAM)<=dot_prod_dict(vectorAB, vectorAB)) & (0<=dot_prod_dict(vectorBC, vectorBM)<=dot_prod_dict(vectorBC, vectorBC))

def calc_obj_coords(x,z,dx,dz,rotation):
    """Returns an array of points that are the coordinates of the rectangle """
    radian_amount = rotation*math.pi/180.0

    rotate_sin = math.sin(radian_amount)
    rotate_cos = math.cos(radian_amount)
    a = { 'x': x+(dx*rotate_cos)-(dz*rotate_sin) , 'y' : 0 , 'z': z+(dx*rotate_sin+dz*rotate_cos)}
    b = { 'x': x+(dx*rotate_cos)-(dz*rotate_sin) , 'y' : 0 , 'z': z-(dx*rotate_sin+dz*rotate_cos)}
    c = { 'x': x-(dx*rotate_cos)+(dz*rotate_sin) , 'y' : 0 , 'z': z-(dx*rotate_sin+dz*rotate_cos)}
    d = { 'x': x-(dx*rotate_cos)+(dz*rotate_sin) , 'y' : 0 , 'z': z+(dx*rotate_sin+dz*rotate_cos)} 
    return [a, b, c, d]
        
def calc_obj_pos( performer_position, other_rects , new_object, old_object):
    """Returns True if we can place the object in the frame, False otherwise. """
        
    dx = old_object['dimensions']['x']
    dz = old_object['dimensions']['z']

    tries = 0
    while tries< MAX_TRIES:
        rotation = random_rotation()
        new_x = random_position()
        new_z = random_position()
        
        rect = calc_obj_coords(new_x, new_z, dx, dz, rotation)
        if not collision(rect, performer_position) and (len(other_rects) == 0 or any(sat_entry(rect, other_rect) for other_rect in other_rects)):
            break          
        tries += 1
     
    if tries < MAX_TRIES :
        new_object['rotation'] = { 'x' : 0, 'y': rotation, 'z': 0 }
        new_object['position'] = { 'x' : new_x, 'y': old_object['position_y'], 'z' : new_z}
        other_rects.append(rect)
        return True
    
    return False

def generate_file(name, objects): 
    global OUTPUT_TEMPLATE
    body = copy.deepcopy(OUTPUT_TEMPLATE)
    body['name'] = os.path.basename(name)
    body['ceilingMaterial'] = random.choice(CEILING_AND_WALL_MATERIALS)
    body['wallMaterial'] = random.choice(CEILING_AND_WALL_MATERIALS)
    body['floorMaterial'] =random.choice(FLOOR_MATERIALS)
    position = body['performerStart']['position']
    position['x'] = random_position()
    position['y'] = 0
    position['z'] = random_position()
    body['performerStart']['rotation']['y'] = random_rotation()
    
    other_rects = [ ]
    object_count = random.randint(1,MAX_OBJECTS)
    for x in range (0, object_count):
        selected_object = copy.deepcopy(random.choice(objects))
        shows_object = {}
    
        if calc_obj_pos(position, other_rects, shows_object, selected_object):
            new_object = {}
            new_object['id'] = selected_object['type']+'_'+str(uuid.uuid4())
            new_object['type'] = selected_object['type']
            new_object['info'] = selected_object['info']
            new_object['mass'] = selected_object['mass']
            #new_object['dimensions'] = selected_object['dimensions']
            for attribute in selected_object['attributes']:
                new_object[attribute]= True
    
            shows = [shows_object]
            new_object['shows'] = shows;
            shows_object['stepBegin'] = 0;
            shows_object['scale'] = selected_object['scale']
            if 'salientMaterials' in selected_object:
                salientMaterialsIndex = selected_object['salientMaterials'][0].upper()+'_MATERIALS'
                salientMaterial = random.choice(globals().get(salientMaterialsIndex, None))
                new_object['material']=salientMaterial;
                new_object['info'].append(selected_object['salientMaterials'][0])
                new_object['salientMaterials'] = selected_object['salientMaterials']
            body['objects'].append(new_object)
        
    with open(name, 'w') as out:
        json.dump(body, out, indent=2)



def generate_one_fileset(prefix, count, objects):
    # skip existing files
    index = 1
    dirname = os.path.dirname(prefix)
    if dirname != '':
        os.makedirs(dirname, exist_ok=True)

    while count > 0:
        file_exists = True
        while file_exists:
            name = f'{prefix}-{index:04}.json'
            file_exists = os.path.exists(name)
            index += 1

        generate_file(name,objects)
        count -= 1


def main(argv):
    parser = argparse.ArgumentParser(description='Create one or more scene descriptions')
    parser.add_argument('--prefix', required=True, help='Prefix for output filenames')
    parser.add_argument('-c', '--count', type=int, default=1, help='How many scenes to generate [default=1]')
    parser.add_argument('--seed', type=int, default=None, help='Random number seed [default=None]')
    parser.add_argument('--objects', required=True, help='File containing a list of objects to insert')
    
    args = parser.parse_args(argv[1:])
    random.seed(args.seed)       
    objects = load_object_file(args.objects)
    generate_one_fileset(args.prefix, args.count, objects)

    

if __name__ == '__main__':
    main(sys.argv)
