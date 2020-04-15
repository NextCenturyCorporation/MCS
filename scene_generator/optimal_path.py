from extremitypathfinder.extremitypathfinder import PolygonEnvironment as Environment

from  geometry import MAX_SCENE_POSITION, MIN_SCENE_POSITION



# passing the other_rects from my  calculations previously
# This is the source for extremitypathfinder: https://github.com/MrMinimal64/extremitypathfinder
#other_loc will probably contain the target- we'll see
def generatepath(source_loc, target_loc, other_rects):
    '''Boundary has to be CCW, Holes CW'''
    boundary_coordinates = [ (MAX_SCENE_POSITION, MAX_SCENE_POSITION),(MIN_SCENE_POSITION, MAX_SCENE_POSITION),(MIN_SCENE_POSITION, MIN_SCENE_POSITION), (MAX_SCENE_POSITION,MIN_SCENE_POSITION)]
    holes= []
    # This way does make me a bit nervous- as this is coding
    #need to convert to lists of points 
    for object in other_rects:            
        holes.append([(point['x'],point['z']) for point in object])
        
        
    environment = Environment()
    environment.store(boundary_coordinates, holes, validate = True)
    environment.prepare()
    
    return environment.find_shortest_path(source_loc, target_loc)