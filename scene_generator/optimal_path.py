from extremitypathfinder.extremitypathfinder import PolygonEnvironment as Environment

from scene_generator import *



# objecs passed because I forgot to record the dimensions :P
# This is the source for extremitypathfinder: https://github.com/MrMinimal64/extremitypathfinder
def generatepath(body, objects):
    '''Boundary has to be CCW, Holes CW'''
    boundary_coordinates = [ (MAX_SCENE_POSITION, MAX_SCENE_POSITION),(MIN_SCENE_POSITION, MAX_SCENE_POSITION),(MIN_SCENE_POSITION, MIN_SCENE_POSITION), (MAX_SCENE_POSITION,MIN_SCENE_POSITION)]
    
    holes= []
    # This way does make me a bit nervous- as this is coding 
    for object in body['objects']:
        #Handle walls first
        if object['type'] == 'cube':
            dimensions = object['shows'][0]['scale']
            position = object['shows'][0]['position']
            rotation = object['shows'][0]['rotation']
            points = calc_obj_coords(position['x'],position['z'], dimensions['x'],dimensions['z'],rotation['y'])
       
        else:
            type = object['type']
                    
        holes.append([(point['x'],point['z']) for point in points])