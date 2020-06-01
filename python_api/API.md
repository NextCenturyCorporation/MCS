# MCS Python Library: API

- [Python Class: MCS](#mcs)
- [Python Class: MCS_Controller](#mcs_controller)
- [Python Class: MCS_Goal](#mcs_goal)
- [Python Class: MCS_Object](#mcs_object)
- [Python Class: MCS_Step_Output](#mcs_step_output)
- [Actions](#actions)
- [Future Actions (Not Yet Supported)](#future-actions)
- [Goal Descriptions](#goal-description)
- [Goal Metadata](#goal-metadata)

## MCS

### static create_controller(unity_app_file_path)

Creates and returns an MCS Controller object using the Unity application at the given file path.

#### Parameters

- unity_app_file_path : string\
The file path to the MCS Unity application. The TA2 team will give you this application.

#### Returns

- controller : MCS_Controller\
The MCS controller object.

### static load_config_json_file(config_json_file_path)

Reads and returns the data from the given JSON scene configuration file.

#### Parameters

- config_json_file_path : string\
The file path to the MCS scene configuration JSON file. The TA2 team will give you these files, or you can make them yourself (more details on how to do this are coming soon).

#### Returns

- config_data : dict\
The MCS scene configuration data object.

## MCS_Controller

### end_scene([choice, confidence])

Ends the current MCS scene.

#### Parameters

- choice : string, optional\
Your selected choice for IntPhys or classification goals. Not required for goals that have no choices.

- confidence : float, optional\
Your choice confidence (between 0 and 1) for IntPhys or classification goals. Not required for goals that have no choices.

### start_scene(config_data)

Starts a new MCS scene.

#### Parameters

- config_data : dict\
The MCS scene configuration data dict.

#### Returns

- output : MCS_Step_Output\
The MCS scene output data object from the start of the scene.

### step(action[, params])

Runs the given action within the current scene and unpauses the scene’s physics simulation for a few frames.

#### Parameters

- action : string\
Your selected action string from the list of available actions (like "MoveAhead" or "PickupObject").

- params : dict, optional\
Any action-specific parameters.

#### Returns

- output : MCS_Step_Output\
The MCS scene output data object from after the action and the physics simulation were run. Returns None if you have passed the "last_step" of this scene.

## MCS_Goal

### action_list : list of lists of strings, or None

The list of actions that are available for the scene at each step (outer list index).  Each inner list item is a list of action strings. For example, ['MoveAhead','RotateLook,rotation=180'] restricts the actions to either 'MoveAhead' or 'RotateLook' with the 'rotation' parameter set to 180. An action_list of None means that all actions are always available. An empty inner list means that all actions are available for that specific step.

### description : string

A human-readable sentence describing this goal and containing the target task(s) and object(s). Please see [Goal Descriptions](#Goal-Descriptions).

### info_list : list of strings

The list of descriptors of objects and tasks associated with this goal (for the visualization interface).

### last_preview_phase_step : integer

The last step of the Preview Phase in this scene, if any. Each step of a Preview Phase normally has a single specific action defined in this goal's `action_list` property for the performer to choose, like `["Pass"]`. Default: `0` (no preview phase)

### last_step : integer

The last step of this scene. This scene will automatically end following this step.

### task_list : list of strings

The list of tasks associated with this goal (for the visualization interface), secondary to its types.

### type_list : list of strings

The list of types associated with this goal (for the visualization interface), including the relevant MCS core domains.

### metadata : dict

The metadata specific to this goal. Please see [Goal Metadata](#Goal-Metadata).

### answer : dict

The answer specific to this goal, for reinforcement during training. More details coming soon.

## MCS_Object

### uuid : string

The unique ID of this object, used with some actions.

### color : dict

The "r", "g", and "b" pixel values of this object in images from the MCS_Step_Output's "object_mask_list".

### dimensions : list of dicts

The dimensions of this object in the environment's 3D global coordinate system as a list of 8 points (dicts with "x", "y", and "z").

### direction : dict

The direction vector of the "x", "y", and "z" degrees between your position and this object's position (the difference in the two positions), normalized to 1. You can use the "x" and "y" as the "rotation" and "horizon" parameters (respectively) in a "RotateLook" action to face this object.

### distance : float

DEPRECATED. Same as distance_in_steps. Please use distance_in_steps or distance_in_world.

### distance_in_steps : float

The distance from you to this object in number of steps ("Move" actions) on the 2D X/Z movement grid.

### distance_in_world : float

The distance from you to this object in the environment's 3D global coordinate system.

### held : boolean

Whether you are holding this object.

### mass : float

Haptic feedback. The mass of this object.

### material_list : list of strings

Haptic feedback. The material(s) of this object. Possible materials: "Metal", "Wood", "Plastic", "Glass", "Ceramic", "Stone", "Fabric", "Rubber", "Food", "Paper", "Wax", "Soap", "Sponge", "Organic".

### position : dict

The "x", "y", and "z" coordinates for the global position of the center of this object's 3D model.

### rotation : float

This object's rotation angle in degrees.

### visible : boolean

Whether you can see this object in your camera viewport.

## MCS_Step_Output

### action_list : list of strings

The list of all actions (like "MoveAhead" or "PickupObject") that are available for the next step. May be a subset of all possible actions.

### camera_aspect_ratio : (float, float)

The player camera's aspect ratio. This will remain constant for the whole scene.

### camera_clipping_planes : (float, float)

The player camera's near and far clipping planes. This will remain constant for the whole scene.

### camera_field_of_view : float

The player camera's field of view. This will remain constant for the whole scene.

### camera_height : float

The player camera's height. This will change if the player uses actions like "LieDown", "Sit", or "Crouch".

### depth_mask_list : list of Pillow.Image objects

The list of depth mask images from the scene after the last action and physics simulation were run. This is normally a list with five images, where the physics simulation has unpaused and paused again for a little bit between each image, and the final image is the state of the environment before your next action. The MCS_Step_Output object returned from a call to controller.start_scene will normally have a list with only one image, except for a scene with a scripted Preview Phase.

A pixel value of 255 translates to 25 (the far clipping plane) in the environment's global coordinate system.

### goal : MCS_Goal

The goal for the whole scene. Will be None in "Exploration" (a.k.a. "Free Play", or "Playroom") scenes.

### head_tilt : float

How far your head is tilted up/down in degrees (between 90 and -90). Changed by setting the "horizon" parameter in a "RotateLook" action.

### image_list : list of Pillow.Image objects

The list of images from the scene after the last action and physics simulation were run. This is normally a list with five images, where the physics simulation has unpaused and paused again for a little bit between each image, and the final image is the state of the environment before your next action. The MCS_Step_Output object returned from a call to controller.start_scene will normally have a list with only one image, except for a scene with a scripted Preview Phase.

### object_list : list of MCS_Object objects

The list of metadata for all currently visible objects in the scene. For metadata on structural objects like walls, please see `structural_object_list`

### object_mask_list : list of Pillow.Image objects

The list of object mask (instance segmentation) images from the scene after the last action and physics simulation were run. This is normally a list with five images, where the physics simulation has unpaused and paused again for a little bit between each image, and the final image is the state of the environment before your next action. The MCS_Step_Output object returned from a call to controller.start_scene will normally have a list with only one image, except for a scene with a scripted Preview Phase.

The color of each object in the mask corresponds to the "color" property in its MCS_Object object.

### pose : string

Your current pose. Either "LIE", "CRAWL", "SQUAT", or "STAND".

### position : dict

The "x", "y", and "z" coordinates for your global position.

### return_status : string

The return status from your last action.

### reward : int

1 if you have accomplished this scene's goal; 0 otherwise.

### rotation : float

Your current rotation angle in degrees.

### structural_object_list : list of MCS_Object objects

The list of metadata for all the structural objects (like walls) in the scene. This includes occluders and ramps from IntPhys scenes. Please note that occluders are composed of two separate objects, the "wall" and the "pole", with corresponding object IDs (`occluder_wall_<uuid>` and `occluder_pole_<uuid>`), and ramps are composed of between one and three objects (depending on the type of ramp), with corresponding object IDs.

### step_number : integer

The step number of your last action, recorded since you started the current scene.

## Actions

### MoveAhead

Move yourself ahead based on your current viewport.

#### Parameters

- amount : float\
Movement percentage between 0 (no distance) and 1 (maximum distance). Default: 0.5

#### Returns

- "SUCCESSFUL"
- "OBSTRUCTED"\
If you cannot move ahead because your path is obstructed.

### MoveRight

Move yourself to your right based on your current viewport.

#### Parameters

- amount : float\
Movement percentage between 0 (no distance) and 1 (maximum distance). Default: 0.5

#### Returns

- "SUCCESSFUL"
- "OBSTRUCTED"\
If you cannot move ahead because your path is obstructed.

### MoveLeft

Move yourself to your left based on your current viewport.

#### Parameters

- amount : float\
Movement percentage between 0 (no distance) and 1 (maximum distance). Default: 0.5

#### Returns

- "SUCCESSFUL"
- "OBSTRUCTED"\
If you cannot move ahead because your path is obstructed.

### MoveBack

Move yourself back based on your current viewport.

#### Parameters

- amount : float\
Movement percentage between 0 (no distance) and 1 (maximum distance). Default: 0.5

#### Returns

- "SUCCESSFUL"
- "OBSTRUCTED"\
If you cannot move ahead because your path is obstructed.

### RotateLook

Rotate your viewport left/right and/or up/down based on your current viewport.

#### Parameters

- rotation : float\
Rotation degrees around the Y axis to change your look angle (left/right).
- horizon : float\
Rotation degrees around the X axis to change your look angle (up/down). This affects your current "head tilt".

#### Returns

- "SUCCESSFUL"
- "SUCCESSFUL_WITH_INVALID_PARAMETERS"\
If the rotation is not between [-360, 360] or the horizon is not between [-180, 180], 0 will be used in place of each invalid parameter.

### PickupObject

Pickup a nearby object and hold it in your hand. This action incorporates reaching out your hand in front of you, opening your fingers, and grabbing the object.

#### Parameters

- objectId : string, optional\
The "uuid" of the target object. Required unless the "objectDirection" properties are given.
- objectDirectionX : float, optional\
The X of the directional vector pointing to the target object based on your current viewport. Can be used in place of the "objectId" property.
- objectDirectionY : float, optional\
The Y of the directional vector pointing to the target object based on your current viewport. Can be used in place of the "objectId" property.
- objectDirectionZ : float, optional\
The Z of the directional vector pointing to the target object based on your current viewport. Can be used in place of the "objectId" property.

#### Returns

- "SUCCESSFUL"
- "HAND_IS_FULL"\
If you cannot pickup the object because your hand is full.
- "NOT_INTERACTABLE"\
If the object corresponding to the "objectDirection" vector is not an interactable object.
- "NOT_OBJECT"\
If the object corresponding to the "objectId" (or object corresponding to the "objectDirection" vector) is not a real object.
- "NOT_PICKUPABLE"\
If the object itself cannot be picked up.
- "OBSTRUCTED"\
If you cannot pickup the object because your reach is obstructed.
- "OUT_OF_REACH"\
If you cannot pickup the object because you are out of reach.

### PutObject

Place an object you are holding into/onto a nearby receptacle object.

#### Parameters

- objectId : string, optional\
The "uuid" of the held object. Defaults to the first held object.
- receptacleObjectId : string\
The "uuid" of the target receptacle. Required unless the "receptacleObjectDirection" properties are given.
- receptacleObjectDirectionX : float, optional\
The X of the directional vector pointing to the target receptacle based on your current viewport. Can be used in place of the "receptacleObjectId" property.
- receptacleObjectDirectionY : float, optional\
The Y of the directional vector pointing to the target receptacle based on your current viewport. Can be used in place of the "receptacleObjectId" property.
- receptacleObjectDirectionZ : float, optional\
The Z of the directional vector pointing to the target receptacle based on your current viewport. Can be used in place of the "receptacleObjectId" property.

#### Returns

- "SUCCESSFUL"
- "NOT_HELD"\
If you cannot place the object because you are not holding it.
- "NOT_INTERACTABLE"\
If the object corresponding to the "objectDirection" or "receptacleObjectDirection" vectors is not an interactable object.
- "NOT_OBJECT"\
If the object corresponding to the "objectId" or "receptacleObjectId" (or object corresponding to the "objectDirection" or "receptacleObjectDirection" vectors) is not a real object.
- "NOT_RECEPTACLE"\
If the receptacleObjectId is not a receptacle object.
- "OBSTRUCTED"\
If you cannot place the object because your reach is obstructed.
- "OUT_OF_REACH"\
If you cannot place the object because you are out of reach of the receptacle.

### DropObject

Drop an object you are holding.

#### Parameters

- objectId : string, optional\
The "uuid" of the held object. Defaults to the first held object.

#### Returns

- "SUCCESSFUL"
- "NOT_HELD"\
If you cannot drop the object because you are not holding it.
- "NOT_INTERACTABLE"\
If the object corresponding to the "objectDirection" vector is not an interactable object.
- "NOT_OBJECT"\
If the object corresponding to the "objectId" (or object corresponding to the "objectDirection" vector) is not a real object.

### ThrowObject

Throw an object you are holding.

#### Parameters

- objectId : string, optional\
The "uuid" of the held object. Defaults to the first held object.
- objectDirectionX : float, optional\
The X of the directional vector pointing to where you would like to throw the object based on your current viewport.
- objectDirectionY : float, optional\
The Y of the directional vector pointing to where you would like to throw the object based on your current viewport.
- objectDirectionZ : float, optional\
The Z of the directional vector pointing to where you would like to throw the object based on your current viewport.
(Note: if no direction is given, the object will be thrown forward (0, 0, 1))

- force : float\
The amount of force, from 0 to 1, used to throw the held object. Default: 0.5

#### Returns

- "SUCCESSFUL"
- "SUCCESSFUL_WITH_INVALID_PARAMETERS"\
If the rotation is not between [-360, 360] or the horizon is not between [-180, 180], 0 will be used in place of each invalid parameter.
- "NOT_HELD"\
If you cannot drop the object because you are not holding it.
- "NOT_INTERACTABLE"\
If the object corresponding to the "objectDirection" vector is not an interactable object.
- "NOT_OBJECT"\
If the object corresponding to the "objectId" (or object corresponding to the "objectDirection" vector) is not a real object.

### PullObject

Pull a nearby object.

#### Parameters

- objectId : string, optional\
The "uuid" of the target object. Required unless the "objectDirection" properties are given.
- objectDirectionX : float, optional\
The X of the directional vector pointing to the target object based on your current viewport. Can be used in place of the "objectId" property.
- objectDirectionY : float, optional\
The Y of the directional vector pointing to the target object based on your current viewport. Can be used in place of the "objectId" property.
- objectDirectionZ : float, optional\
The Z of the directional vector pointing to the target object based on your current viewport. Can be used in place of the "objectId" property.
- (Not Yet Supported) rotation : float\
Rotation degrees around the Y axis to pull the target object (left/right).
- (Not Yet Supported) horizon : float\
Rotation degrees around the X axis to pull the target object (up/down).
- force : float\
The amount of force, from 0 to 1, used to pull the target object. Default: 0.5

#### Returns

- "SUCCESSFUL"
- "SUCCESSFUL_WITH_INVALID_PARAMETERS"\
If the rotation is not between [-360, 360] or the horizon is not between [-180, 180], 0 will be used in place of each invalid parameter.
- "NOT_INTERACTABLE"\
If the object corresponding to the "objectDirection" vector is not an interactable object.
- "NOT_OBJECT"\
If the object corresponding to the "objectId" (or object corresponding to the "objectDirection" vector) is not a real object.
- "OBSTRUCTED"\
If you cannot pull the object because your reach is obstructed.
- "OUT_OF_REACH"\
If you cannot pull the object because you are out of reach.

### PushObject

Push a nearby object.

#### Parameters

- objectId : string, optional\
The "uuid" of the target object. Required unless the "objectDirection" properties are given.
- objectDirectionX : float, optional\
The X of the directional vector pointing to the target object based on your current viewport. Can be used in place of the "objectId" property.
- objectDirectionY : float, optional\
The Y of the directional vector pointing to the target object based on your current viewport. Can be used in place of the "objectId" property.
- objectDirectionZ : float, optional\
The Z of the directional vector pointing to the target object based on your current viewport. Can be used in place of the "objectId" property.
- (Not Yet Supported) rotation : float\
Rotation degrees around the Y axis to push the target object (left/right).
- (Not Yet Supported) horizon : float\
Rotation degrees around the X axis to push the target object (up/down).
- force : float\
The amount of force, from 0 to 1, used to push the target object. Default: 0.5

#### Returns

- "SUCCESSFUL"
- "SUCCESSFUL_WITH_INVALID_PARAMETERS"\
If the rotation is not between [-360, 360] or the horizon is not between [-180, 180], 0 will be used in place of each invalid parameter.
- "NOT_INTERACTABLE"\
If the object corresponding to the "objectDirection" vector is not an interactable object.
- "NOT_OBJECT"\
If the object corresponding to the "objectId" (or object corresponding to the "objectDirection" vector) is not a real object.
- "OBSTRUCTED"\
If you cannot push the object because your reach is obstructed.
- "OUT_OF_REACH"\
If you cannot push the object because you are out of reach.

### OpenObject

Open a nearby object.

#### Parameters

- objectId : string, optional\
The "uuid" of the target object. Required unless the "objectDirection" properties are given.
- objectDirectionX : float, optional\
The X of the directional vector pointing to the target object based on your current viewport. Can be used in place of the "objectId" property.
- objectDirectionY : float, optional\
The Y of the directional vector pointing to the target object based on your current viewport. Can be used in place of the "objectId" property.
- objectDirectionZ : float, optional\
The Z of the directional vector pointing to the target object based on your current viewport. Can be used in place of the "objectId" property.
- amount : float\
The amount to open the object between 0 (completely closed) and 1 (completely opened). Default: 1

#### Returns

- "SUCCESSFUL"
- "IS_OPENED_COMPLETELY"\
If you cannot open the object because it is completely opened.
- "NOT_INTERACTABLE"\
If the object corresponding to the "objectDirection" vector is not an interactable object.
- "NOT_OBJECT"\
If the object corresponding to the "objectId" (or object corresponding to the "objectDirection" vector) is not a real object.
- "NOT_OPENABLE"\
If you cannot open the object because it is not openable.
- "OUT_OF_REACH"\
If you cannot open the object because you are out of reach.
- "OBSTRUCTED"\
If you cannot open the object because you are obstructed.

### CloseObject

Close a nearby object.

#### Parameters

- objectId : string, optional\
The "uuid" of the target object. Required unless the "objectDirection" properties are given.
- objectDirectionX : float, optional\
The X of the directional vector pointing to the target object based on your current viewport. Can be used in place of the "objectId" property.
- objectDirectionY : float, optional\
The Y of the directional vector pointing to the target object based on your current viewport. Can be used in place of the "objectId" property.
- objectDirectionZ : float, optional\
The Z of the directional vector pointing to the target object based on your current viewport. Can be used in place of the "objectId" property.
- amount : float\
The amount to close the object between 0 (completely opened) and 1 (completely closed). Default: 1

#### Returns

- "SUCCESSFUL"
- "IS_CLOSED_COMPLETELY"\
If you cannot close the object because it is completely closed.
- "NOT_INTERACTABLE"\
If the object corresponding to the "objectDirection" vector is not an interactable object.
- "NOT_OBJECT"\
If the object corresponding to the "objectId" (or object corresponding to the "objectDirection" vector) is not a real object.
- "NOT_OPENABLE"\
If you cannot close the object because it is not openable.
- "OUT_OF_REACH"\
If you cannot close the object because you are out of reach.
- "OBSTRUCTED"\
If you cannot close the object because you are obstructed.

### Pass

Do nothing.

#### Returns

- "SUCCESSFUL"

## Future Actions

(Not Yet Supported)

### LieDown

Change pose to "LIE".

#### Parameters

- rotation : float\
Rotation around the Y axis to change your look angle.

#### Returns

- "SUCCESSFUL"
- "SUCCESSFUL_WITH_INVALID_PARAMETERS"\
If the rotation is not between [-360, 360], 0 will be used in place of the invalid parameter.

### Crawl

Change pose to "CRAWL".

#### Returns

- "SUCCESSFUL"
- "OBSTRUCTED"\
If you cannot enter "CRAWL" pose because your path above you is obstructed.
- "WRONG_POSE"\
If you cannot enter "CRAWL" pose because you not in "LIE" pose face-down or are not in "CRAWL" or "STAND" pose.

### Squat

Change pose to "SQUAT".

#### Returns

- "SUCCESSFUL"
- "OBSTRUCTED"\
If you cannot enter "SQUAT" pose because your path above you is obstructed.
- "WRONG_POSE"\
If you cannot enter "SQUAT" pose because you are not in "CRAWL" or "STAND" pose.

### Stand

Change pose to "STAND".

#### Returns

- "SUCCESSFUL"
- "OBSTRUCTED"\
If you cannot enter "STAND" pose because your path above you is obstructed.
- "WRONG_POSE"\
If you cannot enter "STAND" pose because you are not in "SQUAT" pose.

### RotateObject

Rotate a nearby object.

#### Parameters

- objectId : string, optional\
The "uuid" of the target object. Required unless the "objectDirection" properties are given.
- objectDirectionX : float, optional\
The X of the directional vector pointing to the target object based on your current viewport. Can be used in place of the "objectId" property.
- objectDirectionY : float, optional\
The Y of the directional vector pointing to the target object based on your current viewport. Can be used in place of the "objectId" property.
- objectDirectionZ : float, optional\
The Z of the directional vector pointing to the target object based on your current viewport. Can be used in place of the "objectId" property.
- rotationX : float\
Rotation degrees around the X axis.
- rotationY : float\
Rotation degrees around the Y axis.
- rotationZ : float\
Rotation degrees around the Z axis.

#### Returns

- "SUCCESSFUL"
- "SUCCESSFUL_WITH_INVALID_PARAMETERS"\
If the X, Y, or Z is not between [-360, 360], 0 will be used in place of each invalid parameter.
- "NOT_INTERACTABLE"\
If the object corresponding to the "objectDirection" vector is not an interactable object.
- "NOT_OBJECT"\
If the object corresponding to the "objectId" (or object corresponding to the "objectDirection" vector) is not a real object.

### RotateObjectInHand

Rotate a held object.

#### Parameters

- objectId : string, optional\
The "uuid" of the held object. Required unless the "objectDirection" properties are given.
- objectDirectionX : float, optional\
The X of the directional vector pointing to the target object based on your current viewport. Can be used in place of the "objectId" property.
- objectDirectionY : float, optional\
The Y of the directional vector pointing to the target object based on your current viewport. Can be used in place of the "objectId" property.
- objectDirectionZ : float, optional\
The Z of the directional vector pointing to the target object based on your current viewport. Can be used in place of the "objectId" property.
- rotationX : float\
Rotation degrees around the X axis.
- rotationY : float\
Rotation degrees around the Y axis.
- rotationZ : float\
Rotation degrees around the Z axis.

#### Returns

- "SUCCESSFUL"
- "SUCCESSFUL_WITH_INVALID_PARAMETERS"\
If the X, Y, or Z is not between [-360, 360], 0 will be used in place of each invalid parameter.
- "NOT_HELD"\
If you cannot drop the object because you are not holding it.
- "NOT_INTERACTABLE"\
If the object corresponding to the "objectDirection" vector is not an interactable object.
- "NOT_OBJECT"\
If the object corresponding to the "objectId" (or object corresponding to the "objectDirection" vector) is not a real object.

### BangObject

TODO

### ChangeGrip

TODO

### Cry

TODO

### MoveHand

TODO

### Point

TODO

### Speak

TODO

### Stare

TODO

### SuckOnObject

TODO

### SwatObject

TODO

### SwitchHand

TODO

### ToggleObject

TODO

### WaveObject

TODO

## Goal Descriptions

Objects will be described with the following syntax: `size weight color(s) material(s) object`

Sizes:

- `tiny`: near the size of a baseball
- `small`: near the size of a baby
- `medium`: near the size of a child
- `large`: near the size of an adult
- `huge`: near the size of a sofa

Weights:

- `light`: can be held by a baby
- `heavy`: cannot be held by a baby, but can be pushed or pulled
- `massive`: cannot be moved by a baby

Colors:

- `black`
- `blue`
- `brown`
- `green`
- `grey`
- `orange`
- `purple`
- `red`
- `white`
- `yellow`

Materials:

- `ceramic`
- `food`
- `glass`
- `hollow`
- `fabric`
- `metal`
- `organic`
- `paper`
- `plastic`
- `rubber`
- `soap`
- `sponge`
- `stone`
- `wax`
- `wood`

## Goal Metadata

A goal's `metadata` property is a dict with a string `category` property and one or more other properties depending on the `category`.

Categories:

- [`"INTPHYS"`](#intphys)
- [`"RETRIEVAL"`](#retrieval)
- [`"TRANSFERRAL"`](#transferral)
- [`"TRAVERSAL"`](#traversal)

### IntPhys

In a scenario that has an IntPhys goal, you must sit and observe a scene as objects move across your camera's viewport, and then decide whether the scene is "plausible" or "implausible". These scenarios will demand a "common sense" understanding of basic ("intuitive") physics. Based on Emmanuel Dupoux's [IntPhys: A Benchmark for Visual Intuitive Physics Reasoning](https://intphys.com/).

An IntPhys goal's `metadata` (with `category` of `"INTPHYS"`) will also have the following properties:

#### choose : list of strings

The list of choices, one of which must be given in your call to `end_scene`.  For IntPhys goals, this value will always be `["plausible", "implausible"]`.

### Retrieval

In a scenario that has a retrieval goal, you must find and pickup a target object. This may involve exploring the scene, avoiding obstacles, interacting with objects (like closed containers), and (future evaluations) tracking moving objects. These scenarios will demand a "common sense" understanding of self navigation (how to move and rotate yourself within a scene and around obstacles), object interaction (how objects work, including opening containers), and (future evaluations) the basic physics of movement (kinematics, gravity, friction, etc.).

A retrieval goal's `metadata` (with `category` of `"RETRIEVAL"`) will also have the following properties:

#### target.id : string

The `objectId` of the target object to retrieve.

#### target.image : list of lists of lists of integers

An image of the target object to retrieve, given as a three-dimensional RGB pixel array.

#### target.info : list of strings

Human-readable information describing the target object needed for the visualization interface.

#### target.match_image : string

Whether the image of the target object (`target.image`) exactly matches the actual target object in the scene. If `false`, then the actual object will be different in one way (for example, the image may depict a blue ball, but the actual object is a yellow ball, or a blue cube).

### Transferral

In a scenario that has a transferral goal, you must find and pickup the first target object and put it down either next to or on top of the second target object. This may involve exploring the scene, avoiding obstacles, interacting with objects (like closed receptacles), and (future evaluations) tracking moving objects. These scenarios will demand a "common sense" understanding of self navigation (how to move and rotate yourself within a scene and around obstacles), object interaction (how objects work, including opening containers), and (future evaluations) the basic physics of movement (kinematics, gravity, friction, etc.).

A transferral goal's `metadata` (with `category` of `"TRANSFERRAL"`) will also have the following properties:

#### relationship : list of strings

The required final position of the two target objects in relation to one another.  For transferral goals, this value will always be either `["target_1", "next_to", "target_2"]` or `["target_1", "on_top_of", "target_2"]`.

#### target_1.id : string

The `objectId` of the first target object to pickup and transfer to the second target object.

#### target_1.image : list of lists of lists of integers

An image of the first target object to pickup and transfer to the second target object, given as a three-dimensional RGB pixel array.

#### target_1.info : list of strings

Human-readable information describing the target object needed for the visualization interface.

#### target_1.match_image : string

Whether the image of the first target object (`target_1.image`) exactly matches the actual object in the scene. If `false`, then the actual first target object will be different in one way (for example, the image may depict a blue ball, but the actual object is a yellow ball, or a blue cube).

#### target_2.id : string

The `objectId` of the second target object to which the first target object must be transferred.

#### target_2.image : list of lists of lists of integers

An image of the second target object to which the first target object must be transferred, given as a three-dimensional RGB pixel array.

#### target_2.info : list of strings

Human-readable information describing the target object needed for the visualization interface.

#### target_2.match_image : string

Whether the image of the second target object (`target_2.image`) exactly matches the actual object in the scene. If `false`, then the actual second target object will be different in one way (for example, the image may depict a blue ball, but the actual object is a yellow ball, or a blue cube).

### Traversal

In a scenario that has a traversal goal, you must find and move next to a target object. This may involve exploring the scene, and avoiding obstacles. These scenarios will demand a "common sense" understanding of self navigation (how to move and rotate yourself within a scene and around obstacles).

A retrieval goal's `metadata` (with `category` of `"TRAVERSAL"`) will also have the following properties:

#### target.id : string

The `objectId` of the target object to find and move next to.

#### target.image : list of lists of lists of integers

An image of the target object to find and move next to, given as a three-dimensional RGB pixel array.

#### target.info : list of strings

Human-readable information describing the target object needed for the visualization interface.

#### target.match_image : string

Whether the image of the target object (`target.image`) exactly matches the actual target object in the scene. If `false`, then the actual object will be different in one way (for example, the image may depict a blue ball, but the actual object is a yellow ball, or a blue cube).
