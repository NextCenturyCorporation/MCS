# MCS Python Library API


* [MCS](#MCS)


* [Controller](#Controller)


* [GoalMetadata](#GoalMetadata)


* [ObjectMetadata](#ObjectMetadata)


* [StepMetadata](#StepMetadata)


* [Actions](#Actions)


* [Goals](#Goals)


* [Materials](#Materials)

## MCS


### class machine_common_sense.mcs.MCS()
Defines utility functions for machine learning modules to create MCS
controllers and handle config data files.


#### static create_controller(unity_app_file_path, debug=False, enable_noise=False, seed=None, size=None, depth_masks=False, object_masks=False)
Creates and returns a new MCS Controller object.


* **Parameters**

    
    * **unity_app_file_path** (*str*) – The file path to your MCS Unity application.


    * **debug** (*boolean**, **optional*) – Whether to save MCS output debug files in this folder.
    (default False)


    * **enable_noise** (*boolean**, **optional*) – Whether to add random noise to the numerical amounts in movement
    and object interaction action parameters.
    (default False)


    * **seed** (*int**, **optional*) – A seed for the Python random number generator.
    (default None)



* **Returns**

    The MCS Controller object.



* **Return type**

    Controller



#### static load_config_json_file(config_json_file_path)
Loads the given JSON config file and returns its data.


* **Parameters**

    **config_json_file_path** (*str*) – The file path to your MCS JSON scene configuration file.



* **Returns**

    
    * *dict* – The MCS scene configuration data from the given JSON file.


    * *None or string* – The error status (if any).



## Controller


### class machine_common_sense.controller.Controller()
Starts and ends scenes, runs actions on each step, and returns scene
output data.


#### end_scene(choice, confidence=1.0)
Ends the current scene.


* **Parameters**

    
    * **choice** (*string**, **optional*) – The selected choice required for ending scenes with
    violation-of-expectation or classification goals.
    Is not required for other goals. (default None)


    * **confidence** (*float**, **optional*) – The choice confidence between 0 and 1 required for ending scenes
    with violation-of-expectation or classification goals.
    Is not required for other goals. (default None)



#### generate_noise()
Returns a random value between -0.05 and 0.05 used to add noise to all
numerical action parameters enable_noise is True.


* **Returns**

    A value between -0.05 and 0.05 (using random.uniform).



* **Return type**

    float



#### start_scene(config_data)
Starts a new scene using the given scene configuration data dict and
returns the scene output data object.


* **Parameters**

    **config_data** (*dict*) – The MCS scene configuration data for the scene to start.



* **Returns**

    The output data object from the start of the scene (the output from
    an “Initialize” action).



* **Return type**

    StepMetadata



#### step(action: str, choice: str = None, confidence: float = None, violations_xy_list: List[Dict[str, float]] = None, heatmap_img: PIL.Image.Image = None, internal_state: object = None, \*\*kwargs)
Runs the given action within the current scene and unpauses the scene’s
physics simulation for a few frames. Can also optionally send
information about scene plausability if applicable.


* **Parameters**

    
    * **action** (*string*) – A selected action string from the list of available actions.


    * **choice** (*string**, **optional*) – The selected choice required by the end of scenes with
    violation-of-expectation or classification goals.
    Is not required for other goals. (default None)


    * **confidence** (*float**, **optional*) – The choice confidence between 0 and 1 required by the end of
    scenes with violation-of-expectation or classification goals.
    Is not required for other goals. (default None)


    * **violations_xy_list** (*List**[**Dict**[**str**, **float**]**]**, **optional*) – A list of one or more (x, y) locations (ex: [{“x”: 1, “y”: 3.4}]),
    each representing a potential violation-of-expectation. Required
    on each step for passive tasks. (default None)


    * **heatmap_img** (*PIL.Image.Image**, **optional*) – An image representing scene plausiblility at a particular
    moment. Will be saved as a .png type. (default None)


    * **internal_state** (*object**, **optional*) – A properly formatted json object representing various kinds of
    internal states at a particular moment. Examples include the
    estimated position of the agent, current map of the world, etc.
    (default None)


    * **\*\*kwargs** – Zero or more key-and-value parameters for the action.



* **Returns**

    The MCS output data object from after the selected action and the
    physics simulation were run. Returns None if you have passed the
    “last_step” of this scene.



* **Return type**

    StepMetadata


## GoalMetadata


### class machine_common_sense.goal_metadata.GoalMetadata(action_list=None, category='', description='', domain_list=None, info_list=None, last_preview_phase_step=0, last_step=None, type_list=None, metadata=None)
Defines metadata for a goal in the MCS 3D environment.


* **Variables**

    
    * **action_list** (*list of lists of strings**, or **None*) – The list of actions that are available for the scene at each step
    (outer list index).  Each inner list item is a list of action strings.
    For example, [‘MoveAhead’,’RotateLook,rotation=180’] restricts the
    actions to either ‘MoveAhead’ or ‘RotateLook’ with the ‘rotation’
    parameter set to 180. An action_list of None means that all
    actions are always available. An empty inner list means that all
    actions are available for that specific step.


    * **category** (*string*) – The category that describes this goal and the properties in its
    metadata. See [Goals](#Goals).


    * **description** (*string*) – A human-readable sentence describing this goal and containing
    the target task(s) and object(s).

    Sizes:
    - tiny: near the size of a baseball
    - small: near the size of a baby
    - medium: near the size of a child
    - large: near the size of an adult
    - huge: near the size of a sofa

    Weights:
    - light: can be held by a baby
    - heavy: cannot be held by a baby, but can be pushed or pulled
    - massive: cannot be moved by a baby

    Colors:
    black, blue, brown, green, grey, orange, purple, red, white, yellow

    Materials:
    See [Materials](#Materials).



    * **domain_list** (*list of strings*) – The list of MCS “core domains” associated with this goal (for the
    visualization interface).


    * **info_list** (*list*) – The list of information for the visualization interface associated
    with this goal.


    * **last_preview_phase_step** (*integer*) – The last step of the Preview Phase of this scene, if a Preview Phase is
    scripted in the scene configuration. Each step of a Preview Phase
    normally has a single specific action defined in this goal’s
    action_list property for the performer to choose, like [‘Pass’].
    Default: 0 (no Preview Phase)


    * **last_step** (*integer*) – The last step of this scene. This scene will automatically end
    following this step.


    * **type_list** (*list of strings*) – The list of types associated with this goal (for the
    visualization interface).


    * **metadata** (*dict*) – The metadata specific to this goal. See [Goals](#Goals).


## ObjectMetadata


### class machine_common_sense.object_metadata.ObjectMetadata(uuid='', color=None, dimensions=None, direction=None, distance=- 1.0, distance_in_steps=- 1.0, distance_in_world=- 1.0, held=False, mass=0.0, material_list=None, position=None, rotation=None, shape='', texture_color_list=None, visible=False)
Defines metadata for an object in the MCS 3D environment.


* **Variables**

    
    * **uuid** (*string*) – The unique ID of this object, used with some actions.


    * **color** (*dict*) – The “r”, “g”, and “b” pixel values of this object in images from the
    StepMetadata’s “object_mask_list”.


    * **dimensions** (*dict*) – The dimensions of this object in the environment’s 3D global
    coordinate system as a list of 8 points (dicts with “x”, “y”, and “z”).


    * **direction** (*dict*) – The direction vector of “x”, “y”, and “z” degrees between your position
    and this object’s position (the difference in the two positions),
    normalized to 1. You can use the “x” and “y” as the “rotation” and
    “horizon” parameters (respectively) in a “RotateLook” action to face
    this object.


    * **distance** (*float*) – DEPRECATED. Same as distance_in_steps. Please use distance_in_steps
    or distance_in_world.


    * **distance_in_steps** (*float*) – The distance from you to this object in number of steps (“Move”
    actions) on the 2D X/Z movement grid.


    * **distance_in_world** (*float*) – The distance from you to this object in the environment’s 3D global
    coordinate system.


    * **held** (*boolean*) – Whether you are holding this object.


    * **mass** (*float*) – Haptic feedback. The mass of this object.


    * **material_list** (*list of strings*) – Haptic feedback. The material(s) of this object.
    See [Materials](#Materials).


    * **position** (*dict*) – The “x”, “y”, and “z” coordinates for the global position of the
    center of this object’s 3D model.


    * **rotation** (*dict*) – This object’s rotation angles around the “x”, “y”, and “z” axes
    in degrees.


    * **shape** (*string*) – This object’s shape in plain English.


    * **texture_color_list** (*list of strings*) – This object’s colors, derived from its textures, in plain English.


    * **visible** (*boolean*) – Whether you can see this object in your camera viewport.


## StepMetadata


### class machine_common_sense.step_metadata.StepMetadata(action_list=None, camera_aspect_ratio=None, camera_clipping_planes=None, camera_field_of_view=0.0, camera_height=0.0, depth_mask_list=None, goal=None, head_tilt=0.0, image_list=None, object_list=None, object_mask_list=None, pose='UNDEFINED', position=None, return_status='UNDEFINED', reward=0, rotation=0.0, step_number=0, structural_object_list=None)
Defines output metadata from an action step in the MCS 3D environment.


* **Variables**

    
    * **action_list** (*list of strings*) – The list of all actions that are available for the next step.
    May be a subset of all possible actions. See [Actions](#Actions).


    * **camera_aspect_ratio** (*(**float**, **float**)*) – The player camera’s aspect ratio. This will remain constant for the
    whole scene.


    * **camera_clipping_planes** (*(**float**, **float**)*) – The player camera’s near and far clipping planes. This will remain
    constant for the whole scene.


    * **camera_field_of_view** (*float*) – The player camera’s field of view. This will remain constant for
    the whole scene.


    * **camera_height** (*float*) – The player camera’s height. This will change if the player uses
    actions like “LieDown”, “Stand”, or “Crawl”.


    * **depth_mask_list** (*list of Pillow.Image objects*) – The list of depth mask images from the scene after the last
    action and physics simulation were run.
    This is normally a list with five images, where the physics simulation
    has unpaused and paused again for a little bit between each image,
    and the final image is the state of the environment before your
    next action. The StepMetadata object returned from a call to
    controller.start_scene will normally have a list with only one image,
    except for a scene with a scripted Preview Phase. A pixel value of
    255 translates to 25 (the far clipping plane) in the environment’s
    global coordinate system.


    * **goal** (*GoalMetadata** or **None*) – The goal for the whole scene. Will be None in “Exploration” scenes.


    * **head_tilt** (*float*) – How far your head is tilted up/down in degrees (between 90 and -90).
    Changed by setting the “horizon” parameter in a “RotateLook” action.


    * **image_list** (*list of Pillow.Image objects*) – The list of images from the scene after the last action and physics
    simulation were run. This is normally a list with five images, where
    the physics simulation has unpaused and paused again for a little
    bit between each image, and the final image is the state of the
    environment before your next action. The StepMetadata object
    returned from a call to controller.start_scene will normally have a
    listwith only one image, except for a scene with a scripted Preview
    Phase.


    * **object_list** (*list of ObjectMetadata objects*) – The list of metadata for all the visible interactive objects in the
    scene. For metadata on structural objects like walls, please see
    structural_object_list


    * **object_mask_list** (*list of Pillow.Image objects*) – The list of object mask (instance segmentation) images from the scene
    after the last action and physics simulation were run. This is
    normally a list with five images, where the physics simulation
    has unpaused and paused again for a little bit between each image,
    and the final image is the state of the environment before your next
    action. The StepMetadata object returned from a call to
    controller.start_scene will normally have a list with only one image,
    except for a scene with a scripted Preview Phase. The color of each
    object in the mask corresponds to the “color” property in its
    ObjectMetadata object.


    * **pose** (*string*) – Your current pose. Either “STANDING”, “CRAWLING”, or “LYING”.


    * **position** (*dict*) – The “x”, “y”, and “z” coordinates for your global position.


    * **return_status** (*string*) – The return status from your last action. See [Actions](#Actions).


    * **reward** (*integer*) – Reward is 1 on successful completion of a task, 0 otherwise.


    * **rotation** (*float*) – Your current rotation angle in degrees.


    * **step_number** (*integer*) – The step number of your last action, recorded since you started the
    current scene.


    * **structural_object_list** (*list of ObjectMetadata objects*) – The list of metadata for all the visible structural objects (like
    walls, occluders, and ramps) in the scene. Please note that occluders
    are composed of two separate objects, the “wall” and the “pole”, with
    corresponding object IDs (occluder_wall_<uuid> and
    occluder_pole_<uuid>), and ramps are composed of between one and three
    objects (depending on the type of ramp), with corresponding object IDs.


## Actions


### class machine_common_sense.action.Action(value)
The actions available in the MCS simulation environment.


#### CLOSE_OBJECT( = 'CloseObject')
Close a nearby object.


* **Parameters**

    
    * **objectId** (*string**, **optional*) – The “uuid” of the target object. Required unless the “objectDirection”
    properties are given.


    * **objectDirectionX** (*float**, **optional*) – The X of the directional vector pointing to the target object based on
    your current viewport. Can be used in place of the “objectId” property.


    * **objectDirectionY** (*float**, **optional*) – The Y of the directional vector pointing to the target object based on
    your current viewport. Can be used in place of the “objectId” property.


    * **objectDirectionZ** (*float**, **optional*) – The Z of the directional vector pointing to the target object based on
    your current viewport. Can be used in place of the “objectId” property.


    * **amount** (*float*) – The amount to close the object between 0 (completely opened) and 1
    (completely closed). Default: 1



* **Returns**

    
    * *“SUCCESSFUL”* – Action successful.


    * *”IS_CLOSED_COMPLETELY”* – If the object is completely closed.


    * *”NOT_INTERACTABLE”* – If the object corresponding to the “objectDirection” vector is not an
    interactable object.


    * *”NOT_OBJECT”* – If the object corresponding to the “objectId” (or object corresponding
    to the “objectDirection” vector) is not an object.


    * *”NOT_OPENABLE”* – If the object itself cannot be closed.


    * *”OBSTRUCTED”* – If you cannot close the object because your path is obstructed.


    * *”OUT_OF_REACH”* – If you cannot close the object because you are out of reach.


    * *”FAILED”* – Unexpected error; please report immediately to development team.




#### CRAWL( = 'Crawl')
Change pose to “CRAWLING”. Can help you move underneath or over objects.


* **Returns**

    
    * *“SUCCESSFUL”* – Action successful.


    * *”OBSTRUCTED”* – If you cannot enter the pose because the path above you is obstructed.


    * *”FAILED”* – Unexpected error; please report immediately to development team.




#### DROP_OBJECT( = 'DropObject')
Drop an object you are holding.


* **Parameters**

    **objectId** (*string**, **optional*) – The “uuid” of the held object. Defaults to the first held object.



* **Returns**

    
    * *“SUCCESSFUL”* – Action successful.


    * *”NOT_HELD”* – If you cannot put down the object corresponding to the “objectId”
    because you are not holding it.


    * *”NOT_OBJECT”* – If the object corresponding to the “objectId” is not an object.


    * *”FAILED”* – Unexpected error; please report immediately to development team.




#### LIE_DOWN( = 'LieDown')
Change pose to “LYING”. Can help you move underneath objects.


* **Returns**

    
    * *“SUCCESSFUL”* – Action successful.


    * *”FAILED”* – Unexpected error; please report immediately to development team.




#### MOVE_AHEAD( = 'MoveAhead')
Move yourself forward based on your current viewport.


* **Parameters**

    **amount** (*float*) – Movement percentage between 0 (no distance) and 1 (maximum distance).
    (default 0.5)



* **Returns**

    
    * *“SUCCESSFUL”* – Action successful.


    * *”OBSTRUCTED”* – If you cannot move forward because your path is obstructed.


    * *”FAILED”* – Unexpected error; please report immediately to development team.




#### MOVE_BACK( = 'MoveBack')
Move yourself backward based on your current viewport.


* **Parameters**

    **amount** (*float*) – Movement percentage between 0 (no distance) and 1 (maximum distance).
    (default 0.5)



* **Returns**

    
    * *“SUCCESSFUL”* – Action successful.


    * *”OBSTRUCTED”* – If you cannot move backward because your path is obstructed.


    * *”FAILED”* – Unexpected error; please report immediately to development team.




#### MOVE_LEFT( = 'MoveLeft')
Move yourself left based on your current viewport.


* **Parameters**

    **amount** (*float*) – Movement percentage between 0 (no distance) and 1 (maximum distance).
    (default 0.5)



* **Returns**

    
    * *“SUCCESSFUL”* – Action successful.


    * *”OBSTRUCTED”* – If you cannot move left because your path is obstructed.


    * *”FAILED”* – Unexpected error; please report immediately to development team.




#### MOVE_RIGHT( = 'MoveRight')
Move yourself right based on your current viewport.


* **Parameters**

    **amount** (*float*) – Movement percentage between 0 (no distance) and 1 (maximum distance).
    (default 0.5)



* **Returns**

    
    * *“SUCCESSFUL”* – Action successful.


    * *”OBSTRUCTED”* – If you cannot move right because your path is obstructed.


    * *”FAILED”* – Unexpected error; please report immediately to development team.




#### OPEN_OBJECT( = 'OpenObject')
Open a nearby object.


* **Parameters**

    
    * **objectId** (*string**, **optional*) – The “uuid” of the target object. Required unless the “objectDirection”
    properties are given.


    * **objectDirectionX** (*float**, **optional*) – The X of the directional vector pointing to the target object based on
    your current viewport. Can be used in place of the “objectId” property.


    * **objectDirectionY** (*float**, **optional*) – The Y of the directional vector pointing to the target object based on
    your current viewport. Can be used in place of the “objectId” property.


    * **objectDirectionZ** (*float**, **optional*) – The Z of the directional vector pointing to the target object based on
    your current viewport. Can be used in place of the “objectId” property.


    * **amount** (*float*) – The amount to open the object between 0 (completely closed) and 1
    (completely opened). Default: 1



* **Returns**

    
    * *“SUCCESSFUL”* – Action successful.


    * *”IS_OPENED_COMPLETELY”* – If the object is completely opened.


    * *”NOT_INTERACTABLE”* – If the object corresponding to the “objectDirection” vector is not an
    interactable object.


    * *”NOT_OBJECT”* – If the object corresponding to the “objectId” (or object corresponding
    to the “objectDirection” vector) is not an object.


    * *”NOT_OPENABLE”* – If the object itself cannot be opened.


    * *”OBSTRUCTED”* – If you cannot open the object because your path is obstructed.


    * *”OUT_OF_REACH”* – If you cannot open the object because you are out of reach.


    * *”FAILED”* – Unexpected error; please report immediately to development team.




#### PASS( = 'Pass')
Do nothing.


* **Returns**

    
    * *“SUCCESSFUL”* – Action successful.


    * *”FAILED”* – Unexpected error; please report immediately to development team.




#### PICKUP_OBJECT( = 'PickupObject')
Pick up a nearby object and hold it in your hand. This action incorporates
reaching out your hand in front of you, opening your fingers, and grabbing
the object.


* **Parameters**

    
    * **objectId** (*string**, **optional*) – The “uuid” of the target object. Required unless the “objectDirection”
    properties are given.


    * **objectDirectionX** (*float**, **optional*) – The X of the directional vector pointing to the target object based on
    your current viewport. Can be used in place of the “objectId” property.


    * **objectDirectionY** (*float**, **optional*) – The Y of the directional vector pointing to the target object based on
    your current viewport. Can be used in place of the “objectId” property.


    * **objectDirectionZ** (*float**, **optional*) – The Z of the directional vector pointing to the target object based on
    your current viewport. Can be used in place of the “objectId” property.



* **Returns**

    
    * *“SUCCESSFUL”* – Action successful.


    * *”HAND_IS_FULL”* – If you cannot pick up the object because your hand is full.


    * *”NOT_INTERACTABLE”* – If the object corresponding to the “objectDirection” vector is not an
    interactable object.


    * *”NOT_OBJECT”* – If the object corresponding to the “objectId” (or object corresponding
    to the “objectDirection” vector) is not an object.


    * *”NOT_PICKUPABLE”* – If the object itself cannot be picked up.


    * *”OBSTRUCTED”* – If you cannot pick up the object because your path is obstructed.


    * *”OUT_OF_REACH”* – If you cannot pick up the object because you are out of reach.


    * *”FAILED”* – Unexpected error; please report immediately to development team.




#### PULL_OBJECT( = 'PullObject')
Pull a nearby object.


* **Parameters**

    
    * **objectId** (*string**, **optional*) – The “uuid” of the target object. Required unless the “objectDirection”
    properties are given.


    * **objectDirectionX** (*float**, **optional*) – The X of the directional vector pointing to the target object based on
    your current viewport. Can be used in place of the “objectId” property.


    * **objectDirectionY** (*float**, **optional*) – The Y of the directional vector pointing to the target object based on
    your current viewport. Can be used in place of the “objectId” property.


    * **objectDirectionZ** (*float**, **optional*) – The Z of the directional vector pointing to the target object based on
    your current viewport. Can be used in place of the “objectId” property.


    * **force** (*float*) – The amount of force, from 0 to 1, used to move the target object.
    Default: 0.5



* **Returns**

    
    * *“SUCCESSFUL”* – Action successful.


    * *”NOT_INTERACTABLE”* – If the object corresponding to the “objectDirection” vector is not an
    interactable object.


    * *”NOT_OBJECT”* – If the object corresponding to the “objectId” (or object corresponding
    to the “objectDirection” vector) is not an object.


    * *”NOT_PICKUPABLE”* – If the object itself cannot be moved by a baby.


    * *”OBSTRUCTED”* – If you cannot move the object because your path is obstructed.


    * *”OUT_OF_REACH”* – If you cannot move the object because you are out of reach.


    * *”FAILED”* – Unexpected error; please report immediately to development team.




#### PUSH_OBJECT( = 'PushObject')
Push a nearby object.


* **Parameters**

    
    * **objectId** (*string**, **optional*) – The “uuid” of the target object. Required unless the “objectDirection”
    properties are given.


    * **objectDirectionX** (*float**, **optional*) – The X of the directional vector pointing to the target object based on
    your current viewport. Can be used in place of the “objectId” property.


    * **objectDirectionY** (*float**, **optional*) – The Y of the directional vector pointing to the target object based on
    your current viewport. Can be used in place of the “objectId” property.


    * **objectDirectionZ** (*float**, **optional*) – The Z of the directional vector pointing to the target object based on
    your current viewport. Can be used in place of the “objectId” property.


    * **force** (*float*) – The amount of force, from 0 to 1, used to move the target object.
    Default: 0.5



* **Returns**

    
    * *“SUCCESSFUL”* – Action successful.


    * *”NOT_INTERACTABLE”* – If the object corresponding to the “objectDirection” vector is not an
    interactable object.


    * *”NOT_OBJECT”* – If the object corresponding to the “objectId” (or object corresponding
    to the “objectDirection” vector) is not an object.


    * *”NOT_PICKUPABLE”* – If the object itself cannot be moved by a baby.


    * *”OBSTRUCTED”* – If you cannot move the object because your path is obstructed.


    * *”OUT_OF_REACH”* – If you cannot move the object because you are out of reach.


    * *”FAILED”* – Unexpected error; please report immediately to development team.




#### PUT_OBJECT( = 'PutObject')
Put down an object you are holding into/onto a nearby receptacle object. A
receptacle is an object that can hold other objects, like a block, box,
drawer, shelf, or table.


* **Parameters**

    
    * **objectId** (*string**, **optional*) – The “uuid” of the held object. Defaults to the first held object.


    * **receptacleObjectId** (*string**, **optional*) – The “uuid” of the target receptacle. Required unless the
    “receptacleObjectDirection” properties are given.


    * **objectDirectionX** (*float**, **optional*) – The X of the directional vector pointing to the target receptacle based
    on your current viewport. Can be used in place of the
    “receptacleObjectId” property.


    * **objectDirectionY** (*float**, **optional*) – The Y of the directional vector pointing to the target receptacle based
    on your current viewport. Can be used in place of the
    “receptacleObjectId” property.


    * **objectDirectionZ** (*float**, **optional*) – The Z of the directional vector pointing to the target receptacle based
    on your current viewport. Can be used in place of the
    “receptacleObjectId” property.



* **Returns**

    
    * *“SUCCESSFUL”* – Action successful.


    * *”NOT_HELD”* – If you cannot put down the object corresponding to the “objectId”
    because you are not holding it.


    * *”NOT_INTERACTABLE”* – If the object corresponding to the “objectDirection” or
    “receptacleObjectDirection” vector is not an interactable object.


    * *”NOT_OBJECT”* – If the object corresponding to the “objectId” and/or
    “receptacleObjectId” (or object corresponding to the
    “receptacleObjectDirection” vector) is not an object.


    * *”NOT_RECEPTACLE”* – If the object corresponding to the “receptacleObjectId” (or object
    corresponding to the “receptacleObjectDirection” vector) is not a
    receptacle.


    * *”OBSTRUCTED”* – If you cannot put down the object because your path is obstructed.


    * *”OUT_OF_REACH”* – If you cannot put down the object because you are out of reach.


    * *”FAILED”* – Unexpected error; please report immediately to development team.




#### ROTATE_LOOK( = 'RotateLook')
Rotate your viewport left/right and/or up/down based on your current
viewport.


* **Parameters**

    
    * **rotation** (*float*) – Rotation degrees around the Y axis to change your look angle
    (left/right). If the rotation is not between [-360, 360], then 0 will
    be used.


    * **horizon** (*float*) – Rotation degrees around the X axis to change your look angle (up/down).
    This affects your current “head tilt”. If the horizon is not between
    [-90, 90], then 0 will be used.



* **Returns**

    
    * *“SUCCESSFUL”* – Action successful.


    * *”FAILED”* – Unexpected error; please report immediately to development team.




#### STAND( = 'Stand')
Change pose to “STANDING”. Can help you move over objects.


* **Returns**

    
    * *“SUCCESSFUL”* – Action successful.


    * *”OBSTRUCTED”* – If you cannot enter the pose because the path above you is obstructed.


    * *”FAILED”* – Unexpected error; please report immediately to development team.




#### THROW_OBJECT( = 'ThrowObject')
Throw an object you are holding.


* **Parameters**

    
    * **objectId** (*string**, **optional*) – The “uuid” of the held object. Defaults to the first held object.


    * **objectDirectionX** (*float**, **optional*) – The X of the directional vector pointing to where you would like to
    throw the object based on your current viewport.


    * **objectDirectionY** (*float**, **optional*) – The Y of the directional vector pointing to where you would like to
    throw the object based on your current viewport.


    * **objectDirectionZ** (*float**, **optional*) – The Z of the directional vector pointing to where you would like to
    throw the object based on your current viewport.



* **Returns**

    
    * *“SUCCESSFUL”* – Action successful.


    * *”NOT_HELD”* – If you cannot throw the object corresponding to the “objectId”
    because you are not holding it.


    * *”NOT_OBJECT”* – If the object corresponding to the “objectId” is not an object.


    * *”FAILED”* – Unexpected error; please report immediately to development team.



## Goals


### class machine_common_sense.goal_metadata.GoalCategory(value)
Each goal will have a “category” string and a “metadata” dict with one or
more properties depending on the “category”.


#### INTPHYS( = 'intphys')
In a scenario that has an IntPhys goal, you must sit and observe a scene as
objects move across your camera’s viewport, and then decide whether the
scene is “plausible” or “implausible”. These scenarios will demand a
“common sense” understanding of basic (“intuitive”) physics. Based on
Emmanuel Dupoux’s IntPhys: A Benchmark for Visual Intuitive Physics
Reasoning ([http://intphys.com](http://intphys.com)).


* **Parameters**

    **choose** (*list of strings*) – The list of choices, one of which must be given in your call to
    end_scene. For IntPhys goals, this value will always be [“plausible”,
    “implausible”].



#### RETRIEVAL( = 'retrieval')
In a scenario that has a retrieval goal, you must find and pickup a target
object. This may involve exploring the scene, avoiding obstacles,
interacting with objects (like closed containers), and (future evaluations)
tracking moving objects. These scenarios will demand a “common sense”
understanding of self navigation (how to move and rotate yourself within a
scene and around obstacles), object interaction (how objects work,
including opening containers), and (future evaluations) the basic physics
of movement (kinematics, gravity, friction, etc.).


* **Parameters**

    
    * **target.id** (*string*) – The objectId of the target object to retrieve.


    * **target.image** (*list of lists of lists of integers*) – An image of the target object to retrieve, given as a 3D RGB pixel
    array.


    * **target.info** (*list of strings*) – Human-readable information describing the target object needed for the
    visualization interface.


    * **target.match_image** (*string*) – Whether the image of the target object (target.image) exactly matches
    the actual target object in the scene. If false, then the actual object
    will be different in one way (for example, the image may depict a blue
    ball, but the actual object is a yellow ball, or a blue cube).



#### TRANSFERRAL( = 'transferral')
In a scenario that has a transferral goal, you must find and pickup the
first target object and put it down either next to or on top of the second
target object. This may involve exploring the scene, avoiding obstacles,
interacting with objects (like closed receptacles), and (future
evaluations) tracking moving objects. These scenarios will demand a “common
sense” understanding of self navigation (how to move and rotate yourself
within a scene and around obstacles), object interaction (how objects work,
including opening containers), and (future evaluations) the basic physics
of movement (kinematics, gravity, friction, etc.).


* **Parameters**

    
    * **relationship** (*list of strings*) – The required final position of the two target objects in relation to
    one another. For transferral goals, this value will always be either
    [“target_1”, “next_to”, “target_2”] or [“target_1”, “on_top_of”,
    “target_2”].


    * **target_1.id** (*string*) – The objectId of the first target object to pickup and transfer to the
    second target object.


    * **target_1.image** (*list of lists of lists of integers*) – An image of the first target object to pickup and transfer to the
    second target object, given as a 3D RGB pixel array.


    * **target_1.info** (*list of strings*) – Human-readable information describing the target object needed for the
    visualization interface.


    * **target_1.match_image** (*string*) – Whether the image of the first target object (target_1.image) exactly
    matches the actual object in the scene. If false, then the actual first
    target object will be different in one way (for example, the image may
    depict a blue ball, but the actual object is a yellow ball, or a blue
    cube).


    * **target_2.id** (*string*) – The objectId of the second target object to which the first target
    object must be transferred.


    * **target_2.image** (*list of lists of lists of integers*) – An image of the second target object to which the first target object
    must be transferred, given as a 3D RGB pixel array.


    * **target_2.info** (*list of strings*) – Human-readable information describing the target object needed for the
    visualization interface.


    * **target_2.match_image** (*string*) – Whether the image of the second target object (target_2.image) exactly
    matches the actual object in the scene. If false, then the actual
    second target object will be different in one way (for example, the
    image may depict a blue ball, but the actual object is a yellow ball,
    or a blue cube).



#### TRAVERSAL( = 'traversal')
In a scenario that has a traversal goal, you must find and move next to a
target object. This may involve exploring the scene, and avoiding
obstacles. These scenarios will demand a “common sense” understanding of
self navigation (how to move and rotate yourself within a scene and around
obstacles).


* **Parameters**

    
    * **target.id** (*string*) – The objectId of the target object to find and move next to.


    * **target.image** (*list of lists of lists of integers*) – An image of the target object to find and move next to, given as a 3D
    RGB pixel array.


    * **target.info** (*list of strings*) – Human-readable information describing the target object needed for the
    visualization interface.


    * **target.match_image** (*string*) – Whether the image of the target object (target.image) exactly matches
    the actual target object in the scene. If false, then the actual object
    will be different in one way (for example, the image may depict a blue
    ball, but the actual object is a yellow ball, or a blue cube).


## Materials


### class machine_common_sense.material.Material(value)
Possible materials of objects. An object can have one or more materials.


#### CERAMIC( = 'CERAMIC')

#### FABRIC( = 'FABRIC')

#### FOOD( = 'FOOD')

#### GLASS( = 'GLASS')

#### METAL( = 'METAL')

#### ORGANIC( = 'ORGANIC')

#### PAPER( = 'PAPER')

#### PLASTIC( = 'PLASTIC')

#### RUBBER( = 'RUBBER')

#### SOAP( = 'SOAP')

#### SPONGE( = 'SPONGE')

#### STONE( = 'STONE')

#### UNDEFINED( = 'UNDEFINED')

#### WAX( = 'WAX')

#### WOOD( = 'WOOD')