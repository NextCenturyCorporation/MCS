Scene File Schema
#################

Scenes
======

A **scene** is a JSON object (called a :ref:`scene config<Scene Config>`) that, when passed to the MCS Unity application via the machine_common_sense python library, describes the objects, materials (colors and textures), environmental features, and scripted actions that are present in a specific instance of the MCS 3D simulation environment.

Scene Config
************

Example:

.. code-block:: json

    {
        "name": "Example MCS Scene Configuration",
        "verison": 2,
        "ceilingMaterial": "AI2-THOR/Materials/Walls/Drywall",
        "floorMaterial": "AI2-THOR/Materials/Fabrics/CarpetWhite 3",
        "wallMaterial": "AI2-THOR/Materials/Walls/DrywallBeige",
        "roomDimensions": {
            "x": 10,
            "y": 3,
            "z": 10
        },
        "roomMaterials": {
            "left":"AI2-THOR/Materials/Walls/DrywallGreen",
            "front":"AI2-THOR/Materials/Walls/Drywall4Tiled",
            "right": "AI2-THOR/Materials/Walls/Drywall4Tiled",
            "back": "AI2-THOR/Materials/Walls/Drywall4Tiled"
        },
        "performerStart": {
            "position": {
                "x": -1,
                "z": -1
            },
            "rotation": {
                "x": 0,
                "y": 90
            }
        },
        "objects": [{
            "id": "sofa",
            "type": "sofa_1",
            "mass": 50,
            "shows": [{
                "stepBegin": 0,
                "position": {
                    "x": -2,
                    "y": 0,
                    "z": -4.25
                }
            }]
        }, {
            "id": "ball_a",
            "type": "sphere",
            "mass": 0.05,
            "materials": ["AI2-THOR/Materials/Plastics/BlueRubber"],
            "pickupable": true,
            "salientMaterials": ["plastic"],
            "shows": [{
                "stepBegin": 0,
                "position": {
                    "x": 0,
                    "y": 0.025,
                    "z": 1
                },
                "scale": {
                    "x": 0.025,
                    "y": 0.025,
                    "z": 0.025
                }
            }]
        }]
    }


Each **scene config** has the following properties:

- `ceilingMaterial` (string, optional): The material (color/texture) for the room's ceiling. See the :ref:`material list <Material List>` for options. Default (v0.0.3+): `"AI2-THOR/Materials/Walls/Drywall"`
- `floorMaterial` (string, optional): The material (color/texture) for the room's floor. See the :ref:`material list <Material List>` for options. Default (v0.0.3+): `"AI2-THOR/Materials/Fabrics/CarpetWhite 3"`
- `floorProperties` (:ref:`physics config <Physics Config>`, optional): Enable custom friction, bounciness, and/or drag on the floor. Default: see :ref:`physics config <Physics Config>`.
- `floorTextures` (:ref:`material position config list <Material Position Config>`, optional): A list of materials to apply to specific areas of the room's floor. These materials override the material set by `floorMaterial` for those specific areas. Default: none
- `goal` (:ref:`goal config <Goal Config>`, optional): The goal for the scene. Default: none
- `holes` (:ref:`grid config list <Grid Config>`, optional): The list of X/Z coordinates corresponding to one or more holes in the room's floor. Coordinates must be integers. Holes are always size 1x1 centered on the given X/Z coordinate. Adjacent holes are combined. Y coordinates are ignored. Holes are too deep to escape. Default: none
- `intuitivePhysics` (bool, optional): Specific performer and room setup for intuitive physics scenes.
- `isometric` (bool, optional): Specific performer and room setup for agent scenes.
- `name` (string, required): A unique name for the scene used for our logs. Default: the filename
- `objects` (:ref:`object config <Object Config>` array, optional): The objects for the scene. Default: `[]`
- `performerStart` (:ref:`transform config <Transform Config>`, optional): The starting position and rotation of the performer (the "player"). Only the `position.x`, `position.z`, `rotation.x` (head tilt), and `rotation.y` properties are used. Default: `{ "position": { "x": 0, "z": 0 }, "rotation": { "y": 0 } }`
- `roomDimensions` (Vector3, optional): Specify the size of the room, not including the thickness of walls, floor, and ceiling.  If omitted or set to 0, 0, 0, the default will be used.  Note: There is a maximum visibility which for objects and structures beyond will not be rendered.  Use caution when creating rooms where the maximum distance exceeds this maximum visibility.  The maximum visibility is 15 meters. Default: 10, 3, 10.
- `roomMaterials` (:ref:`room material config <Room Material Config>`, optional): The materials for each individual wall.  For any individual wall not provided, or all outer walls if object is not provided, they will use 'wallMaterial' property.
- `version` (int, optional): The version of this scene configuration. Default: the latest version
- `wallProperties` (:ref:`physics config <Physics Config>`, optional): Enable custom friction, bounciness, and/or drag on the walls. Default: see :ref:`physics config <Physics Config>`.
- `wallMaterial` (string, optional): The material (color/texture) for the room's four outer walls. See the :ref:`material list <Material List>` for options. Default (v0.0.3+): `"AI2-THOR/Materials/Walls/DrywallBeige"`

Object Config
*************

Each **object config** has the following properties:

- `id` (string, required): The object's unique ID.
- `type` (string, required): The object's type from the :ref:`object list <Object List>`.
- `centerOfMass` (:ref:`vector config <Vector Config>`, optional): The object's center of mass/gravity, if not the default. Default: none
- `changeMaterials` (:ref:`change_materials config <Change Materials Config>` array, optional): The steps on which to change the material(s) (colors/textures) used on the object, and the new materials to use. See the :ref:`material list <Material List>` for options. Default: `[]`
- `forces` (:ref:`force config <Force Config>` array, optional): The steps on which to apply `force <https://docs.unity3d.com/ScriptReference/Rigidbody.AddForce.html>`_ to the object. The config `vector` describes the amount of force (in Newtons) to apply in each direction using the global coordinate system. Resets all existing forces on the object to 0 before applying the new force. Default: `[]`
- `ghosts` (:ref:`step begin and end config config <Step Begin And End Config>` array, optional): TBD
- `hides` (:ref:`single step config <Single Step Config>` array, optional): The steps on which to hide the object, completely removing its existence from the scene until it is shown again (see the `shows` property). Useful if you want to have impossible events (spontaneous disappearance). Default: `[]`
- `kinematic` (boolean, optional): If true, the object will ignore all forces including gravity. See Unity's `isKinematic property <https://docs.unity3d.com/ScriptReference/Rigidbody-isKinematic.html>`_. Usually paired with `structure`. Default: `false`
- `locationParent` (string, optional): The `id` of another object in the scene. If given, this object's `shows.position` and `shows.rotation` will both start from the position and rotation of the `locationParent` object rather than from `0`. Default: none
- `mass` (float, optional): The mass of the object, which affects the physics simulation. Default: `1`
- `materials` (string array, optional): The material(s) (colors/textures) of the object. An object `type` may use multiple individual materials; if so, they must be listed in a specific order. Most non-primitive objects already have specific material(s). See the :ref:`material list <Material List>` for options. Default: none
- `materialFile` (string, optional): Deprecated (please use `materials` now). The material (color/texture) of the object. Most non-primitive objects already have specific material(s). See the :ref:`material list <Material List>` for options. Default: none
- `maxAngularVelocity` (force, optional): Override the object's maximum angular velocity in the physics simulation, affecting how it turns and rolls. Default: `7`
- `moveable` (boolean, optional): Whether the object should be moveable, if it is not already moveable based on its `type`. Default: depends on `type`
- `moves` (:ref:`move config<Move Config>` array, optional): The steps on which to move the object, moving it from one position in the scene to another. The config `vector` describes the amount of position to change, added to the object's current position. Useful if you want to move objects that are `kinematic`. A fifth of each move is made over each of the five substeps (five screenshots) during the step. Default: `[]`
- `nullParent` (:ref:`transform config <Transform Config>`, optional): Whether to wrap the object in a null parent object. Useful if you want to rotate an object by a point other than its center point. Default: none
- `openable` (boolean, optional): Whether the object should be openable, if it is not already openable based on its `type`. Default: depends on `type`
- `opened` (boolean, optional): Whether the object should begin opened. Must also be `openable`. Default: `false`
- `openClose` (:ref:`open close config <Open Close Config>`, optional): The steps where an object is opened or closed by the system.  Default: None
- `lips` (:ref:`platform lips config <Platform Lips Config>`, optional): The sides of a platform to add lips. Default: None
- `locked` (boolean, optional): Whether to lock the container at the start of the simulation.  Locked containers cannot be opened.  Default: false
- `physics` (boolean, optional): Whether to enable physics simulation on the object. Automatically `true` if `moveable`, `openable`, `pickupable`, or `receptacle` is `true`. Use `physics` if you want to enable physics but don't want to use any of those other properties. Default: `false`
- `physicsProperties` (:ref:`physics config <Physics Config>`, optional): Enable custom friction, bounciness, and/or drag on the object. Default: see :ref:`physics config <Physics Config>`.
- `pickupable` (boolean, optional): Whether the object should be pickupable, if it is not already openable based on its `type`. Pickupable objects are also automatically `moveable`. Default: depends on `type`
- `receptacle` (boolean, optional): TBD
- `resetCenterOfMass` (boolean, optional): Whether to reset the object's center of mass/gravity to its default value once the object's Y velocity becomes more than 0.1. Default: `false`
- `resizes` (:ref:`size config <Size Config>` array, optional): The steps on which to resize the object. The config `size` is multiplied by the object's current size. Useful if you want to have impossible events (spontaneous resizing). Default: `[]`
- `rotates` (:ref:`move config <Move Config>` array, optional): The steps on which to rotate the object. The config `vector` describes the amount of rotation (in degrees) to change, added to the object's current rotation. Useful if you want to rotate objects that are `kinematic`. A fifth of each move is made over each of the five substeps (five screenshots) during the step. Default: `[]`
- `salientMaterials` (string array, optional)
- `seesaw` (bool, optional): Whether this object should move like a seesaw. Default: `false`
- `shows` (:ref:`show config <Show Config>` array, optional): The steps on which to show the object, adding its existence to the scene. Each object begins hidden within the scene, so each object should have at least one element in its `shows` array to be useful. Default: `[]`
- `shrouds` (:ref:`step begin and end config config <Step Begin And End Config>` array, optional): The steps on which to shroud the object, temporarily making it invisible, but moving with its existing intertia and able to collide with objects. Useful if you want to have impossible events. Default: `[]`
- `states` (string array array, optional): An array of string arrays containing the state label(s) of the object at each step in the scene, returned by the simulation environment in the object's output metadata. Default: `[]`
- `structure` (boolean, optional): Whether the object is a structural part of the environment. Usually paired with `kinematic`. Default: `false`
- `teleports` (:ref:`teleport config <Teleport Config>` array, optional): The steps on which to teleport the object, teleporting it from one position in the scene to another. The config `position` describes the object's end position in global coordinates and is not affected by the object's current position. Useful if you want to have impossible events (spontaneous teleportation). Default: `[]`
- `togglePhysics` (:ref:`single step config <Single Step Config>` array, optional): The steps on which to toggle physics on the object. Useful if you want to have scripted movement in specific parts of the scene. Can work with the `kinematic` property. Default: `[]`
- `torques` (:ref:`force config <Force Config>` array, optional): The steps on which to apply `torque <https://docs.unity3d.com/ScriptReference/Rigidbody.AddTorque.html>`_ to the object. The config `vector` describes the amount of torque (in Newtons) to apply in each direction using the global coordinate system. Resets all existing torques on the object to 0 before applying the new torque. Default: `[]`

Goal Config
***********

Each **goal config** has the following properties:

- `action_list` (string array array, optional): The list of actions that are available for the scene at each step (outer list index).  Each inner list item is a list of action strings. For example, `['MoveAhead','RotateLook,rotation=180']` restricts the actions to either `'MoveAhead'` or `'RotateLook'` with the `'rotation'` parameter set to `180`. An empty outer `action_list` means that all actions are always available. An empty inner list means that all actions are available for that specific step. Default: none
- `info_list` (array, optional): A list of information for the visualization interface associated with this goal. Default: none
- `last_preview_phase_step` (integer, optional): The last step of the preview phase of this scene, if any. Default: -1
- `last_step` (integer, optional): The last step of this scene. This scene will automatically end following this step.
- `metadata` (:ref:`goal metadata config <Goal Metadata Config>`, optional): The metadata specific to this goal. Default: none
- `task_list` (string array, optional): A list of types for the visualization interface associated with this goal, including the relevant MCS core domains. Default: none
- `type_list` (string array, optional) A list of tasks for the visualization interface associated with this goal (secondary to its types).

Goal Metadata Config
********************

Each **goal metadata config** has the following properties:

(Coming soon!)

Change Materials Config
***********************

Each **change materials config** has the following properties:

- `stepBegin` (integer, required): The step on which the action should occur.  Must be non-negative.  A value of `0` means the action will occur during scene initialization.
- `materials` (string array, required): The new materials for the object.

Force Config
************

Each **force config** has the following properties:

- `stepBegin` (integer, required): The step on which the action should begin.  Must be non-negative.  A value of `0` means the action will begin during scene initialization.
- `stepEnd` (integer, required): The step on which the action should end.  Must be equal to or greater than the `stepBegin`.
- `vector` (:ref:`vector config <Vector Config>`, required): The coordinates to describe the movement. Default: `{ "x": 0, "y": 0, "z": 0 }`
- `impulse` (bool, optional): Whether to apply the force using Unity's impulse force mode, rather than the default force mode. Default: `false`
- `relative` (bool, optional): Whether to apply the force using the object's relative coordinate system, rather than the environment's absolute coordinate system. Default: `false`
- `repeat` (bool, optional): Whether to indefinitely repeat this action. Will wait `stepWait` number of steps after `stepEnd`, then will execute this action for `stepEnd - stepBegin + 1` number of steps, then repeat. Default: `false`
- `stepWait` (integer, optional): If `repeat` is `true`, the number of steps to wait after the `stepEnd` before repeating this action. Default: `0`

Grid Config
*************

Each **grid config** has the following properties:

- `x` (integer)
- `z` (integer)

Material Position Config
************************

Each **material position config** has the following properties:

- `material` (string, required): The material to use.
- `positions` (:ref:`grid config list <Grid Config>`): The list of X/Z coordinates corresponding to one or more areas in which to apply the material. Coordinates must be integers. Areas are always size 1x1 centered on the given X/Z coordinate. Adjacent areas are combined. Y coordinates are ignored.

Move Config
***********

Each **move config** has the following properties:

- `stepBegin` (integer, required): The step on which the action should begin.  Must be non-negative.  A value of `0` means the action will begin during scene initialization.
- `stepEnd` (integer, required): The step on which the action should end.  Must be equal to or greater than the `stepBegin`.
- `vector` (:ref:`vector config <Vector Config>`, required): The coordinates to describe the movement. Default: `{ "x": 0, "y": 0, "z": 0 }`
- `repeat` (bool, optional): Whether to indefinitely repeat this action. Will wait `stepWait` number of steps after `stepEnd`, then will execute this action for `stepEnd - stepBegin + 1` number of steps, then repeat. Default: `false`
- `stepWait` (integer, optional): If `repeat` is `true`, the number of steps to wait after the `stepEnd` before repeating this action. Default: `0`

Platform Lips Config
**************

Each **platform lips config** has the following properties:

- `front` (bool, optional): Positive Z axis
- `back` (bool, optional): Negative Z axis
- `left` (bool, optional): Negative X axis
- `right` (bool, optional): Positive X axis

Physics Config
**************

Each **physics config** has the following properties:

- `enable` (bool, optional): Whether to enable customizing ALL physics properties on the object. You must either customize no properties or all of them. Any unset property in this config will automatically be set to `0`, NOT its Unity default (see below). Default: `false`
- `angularDrag` (float, optional): The object's `angular drag <https://docs.unity3d.com/ScriptReference/Rigidbody-angularDrag.html>`_, between 0 and 1. Default: `0`
- `bounciness` (float, optional): The object's `bounciness <https://docs.unity3d.com/ScriptReference/PhysicMaterial-bounciness.html>`_, between 0 and 1. Default: `0`
- `drag` (float, optional): The object's `drag <https://docs.unity3d.com/ScriptReference/Rigidbody-drag.html>`_. Default: `0`
- `dynamicFriction` (float, optional): The object's `dynamic friction <https://docs.unity3d.com/ScriptReference/PhysicMaterial-dynamicFriction.html>`_, between 0 and 1. Default: `0`
- `staticFriction` (float, optional): The object's `static friction <https://docs.unity3d.com/ScriptReference/PhysicMaterial-staticFriction.html>`_, between 0 and 1. Default: `0`

If no physics config is set, or if the physics config is not enabled, the object will have the following Unity defaults:

- Angular Drag: `0.5`
- Bounciness: `0`
- Drag: `0`
- Dynamic Friction: `0.6`
- Static Friction: `0.6`

Show Config
***********

Each **show config** has the following properties:

- `stepBegin` (integer, required): The step on which to show the object.  Must be non-negative.  A value of `0` means the object will be shown during scene initialization.
- `position` (:ref:`vector config <Vector Config>`, optional): The object's position within the environment using the global coordinate system. Default: `{ "x": 0, "y": 0, "z": 0 }`
- `rotation` (:ref:`vector config <Vector Config>`, optional): The object's rotation (in degrees) within the environment using the global coordinate system. Default: `{ "x": 0, "y": 0, "z": 0 }`
- `scale` (:ref:`vector config <Vector Config>`, optional): The object's scale, which is multiplied by its base scale. Default: `{ "x": 1, "y": 1, "z": 1 }`

Size Config
***********

Each **size config** has the following properties:

- `stepBegin` (integer, required): The step on which the action should begin.  Must be non-negative.  A value of `0` means the action will begin during scene initialization.
- `stepEnd` (integer, required): The step on which the action should end.  Must be equal to or greater than the `stepBegin`.
- `size` (:ref:`vector config <Vector Config>`, required): The coordinates to describe the size, which is multiplied by the object's current size. Default: `{ "x": 1, "y": 1, "z": 1 }`
- `repeat` (bool, optional): Whether to indefinitely repeat this action. Will wait `stepWait` number of steps after `stepEnd`, then will execute this action for `stepEnd - stepBegin + 1` number of steps, then repeat. Default: `false`
- `stepWait` (integer, optional): If `repeat` is `true`, the number of steps to wait after the `stepEnd` before repeating this action. Default: `0`

Single Step Config
******************

Each **single step config** has the following properties:

- `stepBegin` (integer, required): The step on which the action should occur.  Must be non-negative.  A value of `0` means the action will occur during scene initialization.

Step Begin and End Config
*************************

Each **step begin and end config** has the following properties:

- `stepBegin` (integer, required): The step on which the action should occur.  Must be non-negative.  A value of `0` means the action will occur during scene initialization.
- `stepEnd` (integer, required): The step on which the action should end.  Must be equal to or greater than the `stepBegin`.
- `repeat` (bool, optional): Whether to indefinitely repeat this action. Will wait `stepWait` number of steps after `stepEnd`, then will execute this action for `stepEnd - stepBegin + 1` number of steps, then repeat. Default: `false`
- `stepWait` (integer, optional): If `repeat` is `true`, the number of steps to wait after the `stepEnd` before repeating this action. Default: `0`

Open Close Config
*****************

Each **Open Close Config** has the following properties:
- `step` (integer, required): The step on which the action should occur.  Must be non-negative.  A value of `0` means the action will occur during scene initialization.
- `open` (boolean, required): If true, the container will be opened, if false, the container will be closed

Teleport Config
***************

Each **teleport config** has the following properties:

- `stepBegin` (integer, required): The step on which the action should begin.  Must be non-negative.  A value of `0` means the action will begin during scene initialization.
- `position` (:ref:`vector config <Vector Config>`, required): The global coordinates to describe the end position. Default: `{ "x": 0, "y": 0, "z": 0 }`

Transform Config
****************

Each **transform config** has the following properties:

- `position` (:ref:`vector config <Vector Config>`, optional): The object's position within the environment using the global coordinate system. Default: `{ "x": 0, "y": 0, "z": 0 }`
- `rotation` (:ref:`vector config <Vector Config>`, optional): The object's rotation (in degrees) within the environment using the global coordinate system. Default: `{ "x": 0, "y": 0, "z": 0 }`
- `scale` (:ref:`vector config <Vector Config>`, optional): The object's scale, which is multiplied by its base scale.  Default: `{ "x": 1, "y": 1, "z": 1 }`

Vector Config
*************

Each **vector config** has the following properties:

- `x` (float, optional)
- `y` (float, optional)
- `z` (float, optional)

Room Material Config
********************

- `left` (string, optional): The material (color/texture) for the room's left outer wall. See the :ref:`material list <Material List>` for options.  If not provided, walls will use 'wallMaterial' property.  Default: none
- `right` (string, optional): The material (color/texture) for the room's right outer wall. See the :ref:`material list <Material List>` for options.  If not provided, walls will use 'wallMaterial' property.  Default: none
- `front` (string, optional): The material (color/texture) for the room's front outer wall. See the :ref:`material list <Material List>` for options.  If not provided, walls will use 'wallMaterial' property.  Default: none
- `back` (string, optional): The material (color/texture) for the room's back outer wall. See the :ref:`material list <Material List>` for options.  If not provided, walls will use 'wallMaterial' property.  Default: none

Object List
===========

Attributes
**********

- Moveable: Can be pushed, pulled, and knocked over. Can be added to object types that are not `moveable` by default.
- Pickupable: Can be picked up with the `PickupObject` action (all pickupable objects are also moveable). Can be added to object types that are not `pickupable` by default.
- Receptacle: Can hold objects with the `PutObject` action.
- Openable: Can be opened with the `OpenObject` action.

Interactable Objects
********************

Some objects have attributes like `receptacle` or `openable` by default. Some objects have restrictions on categories of materials that can be used on them; only the listed categories are allowed. Each object's base size is using a scale of (x=1, y=1, z=1). Most objects will be positioned on top of the floor with `position.y = 0`; objects marked with `(*)` instead bisect the floor and must be offset by half their height.

Small Objects
-------------

All of the following object types have the `pickupable` attribute by default.

.. list-table::
    :header-rows: 1

    * - Object Type
      - Shape
      - Default Mass
      - Receptacle
      - Openable
      - Materials
      - Base Size
      - Details
    * - `"apple_1"`
      - apple
      - 0.25
      - 
      - 
      - none
      - x=0.111,y=0.12,z=0.122
      - 
    * - `"apple_2"`
      - apple
      - 0.25
      - 
      - 
      - none
      - x=0.117,y=0.121,z=0.116
      - 
    * - `"ball"`
      - ball
      - 1
      - 
      - 
      - :ref:`block_blank <Block Materials (Blank)>`, :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`rubber <Rubber Materials>`, :ref:`wood <Wood Materials>`
      - x=1,y=1,z=1
      - 
    * - `"block_blank_blue_cube"`
      - blank block cube
      - 0.66
      - X
      -
      - :ref:`block_blank <Block Materials (Blank)>`, :ref:`wood <Wood Materials>`
      - x=0.1,y=0.1,z=0.1
      -
    * - `"block_blank_blue_cylinder"`
      - blank block cylinder
      - 0.66
      - X
      -
      - :ref:`block_blank <Block Materials (Blank)>`, :ref:`wood <Wood Materials>`
      - x=0.1,y=0.1,z=0.1
      -
    * - `"block_blank_red_cube"`
      - blank block cube
      - 0.66
      - X
      -
      - :ref:`block_blank <Block Materials (Blank)>`, :ref:`wood <Wood Materials>`
      - x=0.1,y=0.1,z=0.1
      -
    * - `"block_blank_red_cylinder"` 
      - blank block cylinder 
      - 0.66
      - X
      -
      - :ref:`block_blank <Block Materials (Blank)>`, :ref:`wood <Wood Materials>`
      - x=0.1,y=0.1,z=0.1
      -
    * - `"block_blank_wood_cube"`
      - blank block cube 
      - 0.66
      - X
      -
      - :ref:`block_blank <Block Materials (Blank)>`, :ref:`wood <Wood Materials>`
      - x=0.1,y=0.1,z=0.1
      -
    * - `"block_blank_wood_cylinder"` 
      - blank block cylinder 
      - 0.66
      - X
      -
      - :ref:`block_blank <Block Materials (Blank)>`, :ref:`wood <Wood Materials>`
      - x=0.1,y=0.1,z=0.1
      -
    * - `"block_blank_yellow_cube"` 
      - blank block cube
      - 0.66
      - X
      -
      - :ref:`block_blank <Block Materials (Blank)>`, :ref:`wood <Wood Materials>`
      - x=0.1,y=0.1,z=0.1
      -
    * - `"block_blank_yellow_cylinder"`
      - blank block cylinder 
      - 0.66
      - X
      -
      - :ref:`block_blank <Block Materials (Blank)>`, :ref:`wood <Wood Materials>`
      - x=0.1,y=0.1,z=0.1
      -
    * - `"block_blue_letter_a"`
      - letter block cube
      - 0.66
      - X
      -
      - :ref:`block_letter_number <Block Materials (Letter/Number)>`, :ref:`wood <Wood Materials>`
      - x=0.1,y=0.1,z=0.1
      -
    * - `"block_blue_letter_b"` 
      - letter block cube 
      - 0.66
      - X
      -
      - :ref:`block_letter_number <Block Materials (Letter/Number)>`, :ref:`wood <Wood Materials>`
      - x=0.1,y=0.1,z=0.1
      -
    * - `"block_blue_letter_c"`
      - letter block cube 
      - 0.66
      - X
      -
      - :ref:`block_letter_number <Block Materials (Letter/Number)>`, :ref:`wood <Wood Materials>`
      - x=0.1,y=0.1,z=0.1
      -
    * - `"block_blue_letter_d"`
      - letter block cube 
      - 0.66
      - X
      -
      - :ref:`block_letter_number <Block Materials (Letter/Number)>`, :ref:`wood <Wood Materials>`
      - x=0.1,y=0.1,z=0.1
      -
    * - `"block_blue_letter_m"`
      - letter block cube 
      - 0.66
      - X
      -
      - :ref:`block_letter_number <Block Materials (Letter/Number)>`, :ref:`wood <Wood Materials>`
      - x=0.1,y=0.1,z=0.1
      -
    * - `"block_blue_letter_s"`
      - letter block cube 
      - 0.66
      - X
      -
      - :ref:`block_letter_number <Block Materials (Letter/Number)>`, :ref:`wood <Wood Materials>`
      - x=0.1,y=0.1,z=0.1
      -
    * - `"block_yellow_number_1"`
      - number block cube 
      - 0.66
      - X
      -
      - :ref:`block_letter_number <Block Materials (Letter/Number)>`, :ref:`wood <Wood Materials>`
      - x=0.1,y=0.1,z=0.1
      -
    * - `"block_yellow_number_2"`
      - number block cube 
      - 0.66
      - X
      -
      - :ref:`block_letter_number <Block Materials (Letter/Number)>`, :ref:`wood <Wood Materials>`
      - x=0.1,y=0.1,z=0.1
      -
    * - `"block_yellow_number_3"`
      - number block cube 
      - 0.66
      - X
      -
      - :ref:`block_letter_number <Block Materials (Letter/Number)>`, :ref:`wood <Wood Materials>`
      - x=0.1,y=0.1,z=0.1
      -
    * - `"block_yellow_number_4"`
      - number block cube 
      - 0.66
      - X
      -
      - :ref:`block_letter_number <Block Materials (Letter/Number)>`, :ref:`wood <Wood Materials>`
      - x=0.1,y=0.1,z=0.1
      -
    * - `"block_yellow_number_5"`
      - number block cube 
      - 0.66
      - X
      -
      - :ref:`block_letter_number <Block Materials (Letter/Number)>`, :ref:`wood <Wood Materials>`
      - x=0.1,y=0.1,z=0.1
      -
    * - `"block_yellow_number_6"`
      - number block cube 
      - 0.66
      - X
      -
      - :ref:`block_letter_number <Block Materials (Letter/Number)>`, :ref:`wood <Wood Materials>`
      - x=0.1,y=0.1,z=0.1
      -
    * - `"bowl_3"`
      - bowl
      - 0.25
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.175,y=0.116,z=0.171
      - 
    * - `"bowl_4"`
      - bowl
      - 0.25
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.209,y=0.059,z=0.206
      - 
    * - `"bowl_6"`
      - bowl
      - 0.25
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.198,y=0.109,z=0.201
      - 
    * - `"car_1"`
      - car
      - 0.5
      - 
      - 
      - :ref:`block_blank <Block Materials (Blank)>`, :ref:`flat <Flat Materials>`, :ref:`wood <Wood Materials>`
      - x=0.075,y=0.065,z=0.14
      - Toy sedan
    * - `"case_1"`
      - case
      - 5
      - X
      - X
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`
      - x=0.71,y=0.19,z=0.42
      - Suitcase. Same as suitcase_1
    * - `"case_3"`
      - case
      - 5
      - X
      - X
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`
      - x=0.81,y=0.21,z=0.56
      - Suitcase
    * - `"crayon_black"`
      - crayon
      - 0.125
      - 
      - 
      - none
      - x=0.01,y=0.085,z=0.01
      - 
    * - `"crayon_blue"`
      - crayon
      - 0.125
      - 
      - 
      - none
      - x=0.01,y=0.085,z=0.01
      - 
    * - `"crayon_green"`
      - crayon
      - 0.125
      - 
      - 
      - none
      - x=0.01,y=0.085,z=0.01
      - 
    * - `"crayon_pink"`
      - crayon
      - 0.125
      - 
      - 
      - none
      - x=0.01,y=0.085,z=0.01
      - 
    * - `"crayon_red"`
      - crayon
      - 0.125
      - 
      - 
      - none
      - x=0.01,y=0.085,z=0.01
      - 
    * - `"crayon_yellow"`
      - crayon
      - 0.125
      - 
      - 
      - none
      - x=0.01,y=0.085,z=0.01
      - 
    * - `"cup_2"`
      - cup
      - 0.25
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.105,y=0.135,z=0.104
      - 
    * - `"cup_3"`
      - cup
      - 0.25
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.123,y=0.149,z=0.126
      - 
    * - `"cup_6"`
      - cup
      - 0.25
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.106,y=0.098,z=0.106
      - 
    * - `"dog_on_wheels"`
      - dog
      - 0.5
      - 
      - 
      - :ref:`block_blank <Block Materials (Blank)>`, :ref:`flat <Flat Materials>`, :ref:`wood <Wood Materials>`
      - x=0.355,y=0.134,z=0.071
      - 
    * - `"duck_on_wheels"`
      - duck
      - 0.5
      - 
      - 
      - :ref:`block_blank <Block Materials (Blank)>`, :ref:`flat <Flat Materials>`, :ref:`wood <Wood Materials>`
      - x=0.21,y=0.17,z=0.065
      - 
    * - `"pacifier"`
      - pacifier
      - 
      - 0.5
      - 
      - none
      - x=0.07,y=0.04,z=0.05
      - 
    * - `"plate_1"`
      - plate
      - 0.25
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.208,y=0.117,z=0.222
      - 
    * - `"plate_3"`
      - plate
      - 0.25
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.304,y=0.208,z=0.305
      - 
    * - `"plate_4"`
      - plate
      - 0.25
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.202,y=0.113,z=0.206
      - 
    * - `"racecar_red"`
      - car
      - 0.5
      - 
      - 
      - :ref:`block_blank <Block Materials (Blank)>`, :ref:`flat <Flat Materials>`, :ref:`wood <Wood Materials>`
      - x=0.07,y=0.06,z=0.15
      - Toy racecar
    * - `"soccer_ball"`
      - ball
      - 0.5
      - 
      - 
      - none
      - x=0.22,y=0.22,z=0.22
      - (*)
    * - `"suitcase_1"`
      - case 
      - 5
      - X
      - X
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`
      - x=0.71,y=0.19,z=0.42
      - Same as case_1
    * - `"train_1"`
      - train
      - 0.5
      - 
      - 
      - :ref:`block_blank <Block Materials (Blank)>`, :ref:`flat <Flat Materials>`, :ref:`wood <Wood Materials>`
      - x=0.16,y=0.2,z=0.23
      - 
    * - `"trolley_1"`
      - trolley
      - 0.5
      - 
      - 
      - :ref:`block_blank <Block Materials (Blank)>`, :ref:`flat <Flat Materials>`, :ref:`wood <Wood Materials>`
      - x=0.16,y=0.2,z=0.23
      - 
    * - `"trophy"`
      - trophy
      - 0.5
      - 
      - 
      - none
      - x=0.19,y=0.3,z=0.14
      - 
    * - `"truck_1"`
      - truck
      - 0.5
      - 
      - 
      - :ref:`block_blank <Block Materials (Blank)>`, :ref:`flat <Flat Materials>`, :ref:`wood <Wood Materials>`
      - x=0.2,y=0.18,z=0.25
      - 
    * - `"turtle_on_wheels"`
      - turtle
      - 
      - 
      - 0.5
      - :ref:`block_blank <Block Materials (Blank)>`, :ref:`flat <Flat Materials>`, :ref:`wood <Wood Materials>`
      - x=0.24,y=0.14,z=0.085
      - 

Furniture Objects
-----------------

.. list-table::
    :header-rows: 1

    * - Object Type
      - Shape
      - Default Mass
      - Moveable
      - Receptacle
      - Openable
      - Materials
      - Base Size
      - Details
    * - `"bookcase_1_shelf"`
      - bookcase
      - 10
      - 
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=1,y=1,z=0.5
      - 
    * - `"bookcase_2_shelf"`
      - bookcase
      - 15
      - 
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=1,y=1.5,z=0.5
      - 
    * - `"bookcase_3_shelf"`
      - bookcase
      - 20
      - 
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=1,y=2,z=0.5
      - 
    * - `"bookcase_4_shelf"`
      - bookcase
      - 25
      - 
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=1,y=2.5,z=0.5
      - 
    * - `"bookcase_1_shelf_sideless"`
      - bookcase
      - 10
      - 
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=1,y=1,z=0.5
      - 
    * - `"bookcase_2_shelf_sideless"`
      - bookcase
      - 15
      - 
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=1,y=1.5,z=0.5
      - 
    * - `"bookcase_3_shelf_sideless"`
      - bookcase
      - 20
      - 
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=1,y=2,z=0.5
      - 
    * - `"bookcase_4_shelf_sideless"`
      - bookcase
      - 25
      - 
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=1,y=2.5,z=0.5
      - 
    * - `"cart_1"`
      - cart
      - 4
      - X
      - X
      - 
      - :ref:`metal <Metal Materials>`
      - x=0.725,y=1.29,z=0.55
      - 
    * - `"chair_1"`
      - chair
      - 5
      - X
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.54,y=1.04,z=0.46
      - 
    * - `"chair_2"`
      - stool
      - 2.5
      - X
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.3,y=0.75,z=0.3
      - 
    * - `"chair_3"`
      - stool
      - 5
      - X
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.42,y=0.8,z=0.63
      - 
    * - `"chair_4"`
      - chair
      - 5
      - X
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`
      - x=0.54,y=0.88,z=0.44
      - 
    * - `"changing_table"`
      - changing table
      - 100
      - 
      - X
      - X
      - :ref:`wood <Wood Materials>`
      - x=1.1,y=0.96,z=0.58
      - 
    * - `"chest_1"`
      - box
      - 15
      - 
      - X
      - X
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.83,y=0.42,z=0.55
      - Rectangular box
    * - `"chest_2"`
      - box
      - 15
      - 
      - X
      - X
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.52,y=0.42,z=0.31
      - Domed chest
    * - `"chest_3"`
      - box
      - 15
      - 
      - X
      - X
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.46,y=0.26,z=0.32
      - Rectangular box
    * - `"chest_8"`
      - box
      - 15
      - 
      - X
      - X
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.42,y=0.32,z=0.36
      - Domed chest
    * - `"crib"`
      - crib
      - 25
      - 
      - 
      - 
      - :ref:`wood <Wood Materials>`
      - x=0.65,y=0.9,z=1.25
      - 
    * - `"shelf_1"`
      - shelf
      - 10
      - 
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.78,y=0.77,z=0.4
      - Object with four cubbies
    * - `"shelf_2"`
      - shelf
      - 20
      - 
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.93,y=0.73,z=1.02
      - Object with three shelves
    * - `"sofa_1"`
      - sofa
      - 100
      - 
      - X
      - 
      - :ref:`sofa_1 <Sofa 1 Materials>`
      - x=2.64,y=1.15,z=1.23
      - 
    * - `"sofa_2"`
      - sofa
      - 100
      - 
      - X
      - 
      - :ref:`sofa_2 <Sofa 2 Materials>`
      - x=2.55,y=1.25,z=0.95
      - 
    * - `"sofa_3"`
      - sofa
      - 100
      - 
      - X
      - 
      - :ref:`sofa_3 <Sofa 3 Materials>`
      - x=2.4,y=1.25,z=0.95
      - 
    * - `"sofa_chair_1"`
      - sofa chair
      - 50
      - 
      - X
      - 
      - :ref:`sofa_chair_1 <Sofa Chair 1 Materials>`
      - x=1.43,y=1.15,z=1.23
      - 
    * - `"sofa_chair_2"`
      - sofa chair
      - 50
      - 
      - X
      - 
      - :ref:`sofa_2 <Sofa 2 Materials>`
      - x=1.425,y=1.25,z=0.95
      - 
    * - `"sofa_chair_3"`
      - sofa chair
      - 50
      - 
      - X
      - 
      - :ref:`sofa_3 <Sofa 3 Materials>`
      - x=1.425,y=1.25,z=0.95
      - 
    * - `"table_1"`
      - table
      - 10
      - X
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.69,y=0.88,z=1.63
      - Rectangular table with legs
    * - `"table_2"`
      - table
      - 5
      - X
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.67,y=0.74,z=0.67
      - Circular table
    * - `"table_3"`
      - table
      - 2.5
      - X
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.573,y=1.018,z=0.557
      - Circular table
    * - `"table_4"`
      - table
      - 5
      - X
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.62,y=0.62,z=1.17
      - Semi-circular table
    * - `"table_5"`
      - table
      - 20
      - X
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`wood <Wood Materials>`
      - x=1.2,y=0.7,z=0.9
      - Rectangular table with sides
    * - `"table_7"`
      - table
      - 10
      - X
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`wood <Wood Materials>`
      - x=1.02,y=0.45,z=0.65
      - Rectangular table with legs
    * - `"table_8"`
      - table
      - 10
      - X
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`wood <Wood Materials>`
      - x=0.65,y=0.71,z=1.02
      - Rectangular table with legs
    * - `"table_11"`
      - table
      - 15
      - X
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=1,y=0.5,z=1
      - Rectangular table with T legs
    * - `"table_12"`
      - table
      - 15
      - X
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=1,y=0.5,z=1
      - Rectangular table with X legs
    * - `"tv_2"`
      - television
      - 5
      - 
      - 
      - 
      - none
      - x=1.234,y=0.896,z=0.256
      - (*)
    * - `"wardrobe"`
      - wardrobe
      - 100
      - 
      - X
      - X
      - :ref:`wood <Wood Materials>`
      - x=1.07,y=2.1,z=0.49
      - 

Primitive Objects
*****************

The following objects have a default mass of 1, base size of (x=1, y=1, z=1), and no material restrictions. You can configure them with properties like `physics`, `moveable`, `pickupable`, or `structure`. These are NOT the internal Unity primitive 3D GameObjects.

- `"circle_frustum"`
- `"cone"`
- `"cube"`
- `"cylinder"`
- `"pyramid"`
- `"sphere"`
- `"square_frustum"`
- `"triangle"`
- `"tube_narrow"`
- `"tube_wide"`

Other Objects
*************

The following objects have a default mass of 1 and no material restrictions. You can configure them with properties like `physics`, `moveable`, `pickupable`, or `structure`.

.. list-table::
    :header-rows: 1

    * - Object Type
      - Base Size
    * - `"cube_hollow_narrow"`
      - (x=1,y=1,z=1)
    * - `"cube_hollow_wide"`
      - (x=1,y=1,z=1)
    * - `"hash"`
      - (x=1,y=1,z=1)
    * - `"letter_l_narrow"`
      - (x=0.5,y=1,z=0.5)
    * - `"letter_l_wide"`
      - (x=1,y=1,z=0.5)
    * - `"letter_l_wide_tall"`
      - (x=1,y=2,z=0.5)
    * - `"letter_x"`
      - (x=1,y=1,z=1)
    * - `"lock_wall"`
      - (x=1,y=1,z=1)

Deprecated Objects
******************

The following object types are not currently used:

* - `"box_2"`
* - `"box_3"`
* - `"box_4"`
* - `"cake"`
* - `"foam_floor_tiles"`
* - `"gift_box_1"`
* - `"painting_2"`
* - `"painting_4"`
* - `"painting_5"`
* - `"painting_9"`
* - `"painting_10"`
* - `"painting_16"`
* - `"plant_1"`
* - `"plant_5"`
* - `"plant_7"`
* - `"plant_9"`
* - `"plant_12"`
* - `"plant_16"`

Child Components
****************

Some objects have child components representing cabinets, drawers, or shelves. Child components are not found in the scene configuration file but are automatically generated by the MCS environment. Child components have their own object IDs so the player may use actions like OpenObject or PutObject with specific cabinets/drawers/shelves.

The following objects have the following child components:

* `"changing_table"`:
    * `"<id>_drawer_top"`
    * `"<id>_drawer_bottom"`
    * `"<id>_shelf_top"`
    * `"<id>_shelf_middle"`
    * `"<id>_shelf_bottom"`
* `"bookcase_1_shelf"`:
    * `"<id>_bottom"`
    * `"<id>_shelf_1"`
* `"bookcase_1_shelf_sideless"`:
    * `"<id>_bottom"`
    * `"<id>_shelf_1"`
* `"bookcase_2_shelf"`:
    * `"<id>_bottom"`
    * `"<id>_shelf_1"`
    * `"<id>_shelf_2"`
* `"bookcase_2_shelf_sideless"`:
    * `"<id>_bottom"`
    * `"<id>_shelf_1"`
    * `"<id>_shelf_2"`
* `"bookcase_3_shelf"`:
    * `"<id>_bottom"`
    * `"<id>_shelf_1"`
    * `"<id>_shelf_2"`
    * `"<id>_shelf_3"`
* `"bookcase_3_shelf_sideless"`:
    * `"<id>_bottom"`
    * `"<id>_shelf_1"`
    * `"<id>_shelf_2"`
    * `"<id>_shelf_3"`
* `"bookcase_4_shelf"`:
    * `"<id>_bottom"`
    * `"<id>_shelf_1"`
    * `"<id>_shelf_2"`
    * `"<id>_shelf_3"`
    * `"<id>_shelf_4"`
* `"bookcase_4_shelf_sideless"`:
    * `"<id>_bottom"`
    * `"<id>_shelf_1"`
    * `"<id>_shelf_2"`
    * `"<id>_shelf_3"`
    * `"<id>_shelf_4"`
* `"shelf_1"`:
    * `"<id>_bottom_left_shelf"`
    * `"<id>_bottom_right_shelf"`
    * `"<id>_top_left_shelf"`
    * `"<id>_top_right_shelf"`
* `"shelf_2"`:
    * `"<id>_middle_shelf"`
    * `"<id>_lower_shelf"`
* `"wardrobe"`:
    * `"<id>_bottom_shelf_left"`
    * `"<id>_left_door"`
    * `"<id>_lower_drawer_bottom_left"`
    * `"<id>_lower_drawer_bottom_right"`
    * `"<id>_lower_drawer_top_left"`
    * `"<id>_lower_drawer_top_right"`
    * `"<id>_middle_shelf_left"`
    * `"<id>_middle_shelf_right"`
    * `"<id>_right_door"`
    * `"<id>_top_shelf"`

Material List
=============

In Unity, "Materials" are the colors and textures applied to objects in the 3D simulation environment. Some objects may have default materials. Some objects may have multiple materials. Some materials may have patterns intended for objects of a specific size, and may look odd if applied to objects that are too big or small.

For our training and evaluation datasets, we normally use the materials under "Walls", "Ceramics", "Fabrics", and "Woods" for the ceiling and the walls, and the materials under "Ceramics", "Fabrics", and "Woods" for the floors.

The following materials are currently available:

Block Materials (Blank)
***********************

Colors that were designed for the blank blocks, and look good on some of the wooden baby toys.

- `"UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/blue_1x1"`
- `"UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/gray_1x1"`
- `"UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/green_1x1"`
- `"UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/red_1x1"`
- `"UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/wood_1x1"`
- `"UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/yellow_1x1"`

Block Materials (Letter/Number)
*******************************

Designs for the letter/number blocks.

- `"UnityAssetStore/KD_NumberBlocks/Assets/Textures/Yellow/TOYBlocks_NumberBlock_1_Yellow_1K/NumberBlockYellow_1"`
- `"UnityAssetStore/KD_NumberBlocks/Assets/Textures/Yellow/TOYBlocks_NumberBlock_2_Yellow_1K/NumberBlockYellow_2"`
- `"UnityAssetStore/KD_NumberBlocks/Assets/Textures/Yellow/TOYBlocks_NumberBlock_3_Yellow_1K/NumberBlockYellow_3"`
- `"UnityAssetStore/KD_NumberBlocks/Assets/Textures/Yellow/TOYBlocks_NumberBlock_4_Yellow_1K/NumberBlockYellow_4"`
- `"UnityAssetStore/KD_NumberBlocks/Assets/Textures/Yellow/TOYBlocks_NumberBlock_5_Yellow_1K/NumberBlockYellow_5"`
- `"UnityAssetStore/KD_NumberBlocks/Assets/Textures/Yellow/TOYBlocks_NumberBlock_6_Yellow_1K/NumberBlockYellow_6"`
- `"UnityAssetStore/KD_AlphabetBlocks/Assets/Textures/Blue/TOYBlocks_AlphabetBlock_A_Blue_1K/ToyBlockBlueA"`
- `"UnityAssetStore/KD_AlphabetBlocks/Assets/Textures/Blue/TOYBlocks_AlphabetBlock_B_Blue_1K/ToyBlockBlueB"`
- `"UnityAssetStore/KD_AlphabetBlocks/Assets/Textures/Blue/TOYBlocks_AlphabetBlock_C_Blue_1K/ToyBlockBlueC"`
- `"UnityAssetStore/KD_AlphabetBlocks/Assets/Textures/Blue/TOYBlocks_AlphabetBlock_D_Blue_1K/ToyBlockBlueD"`
- `"UnityAssetStore/KD_AlphabetBlocks/Assets/Textures/Blue/TOYBlocks_AlphabetBlock_M_Blue_1K/ToyBlockBlueM"`
- `"UnityAssetStore/KD_AlphabetBlocks/Assets/Textures/Blue/TOYBlocks_AlphabetBlock_S_Blue_1K/ToyBlockBlueS"`

Cardboard Materials
*******************

- `"AI2-THOR/Materials/Misc/Cardboard_Brown"`
- `"AI2-THOR/Materials/Misc/Cardboard_Grey"`
- `"AI2-THOR/Materials/Misc/Cardboard_Tan"`

Ceramic Materials
*****************

- `"AI2-THOR/Materials/Ceramics/BrownMarbleFake 1"`
- `"AI2-THOR/Materials/Ceramics/ConcreteBoards1"`
- `"AI2-THOR/Materials/Ceramics/ConcreteFloor"`
- `"AI2-THOR/Materials/Ceramics/GREYGRANITE"`
- `"AI2-THOR/Materials/Ceramics/PinkConcrete_Bedroom1"`
- `"AI2-THOR/Materials/Ceramics/RedBrick"`
- `"AI2-THOR/Materials/Ceramics/TexturesCom_BrickRound0044_1_seamless_S"` (rough stone)
- `"AI2-THOR/Materials/Ceramics/WhiteCountertop"`

Fabric Materials
****************

- `"AI2-THOR/Materials/Fabrics/BedroomCarpet"` (blue pattern)
- `"AI2-THOR/Materials/Fabrics/Carpet2"`
- `"AI2-THOR/Materials/Fabrics/Carpet3"`
- `"AI2-THOR/Materials/Fabrics/Carpet4"`
- `"AI2-THOR/Materials/Fabrics/Carpet8"`
- `"AI2-THOR/Materials/Fabrics/CarpetDark"`
- `"AI2-THOR/Materials/Fabrics/CarpetDark 1"`
- `"AI2-THOR/Materials/Fabrics/CarpetDarkGreen"`
- `"AI2-THOR/Materials/Fabrics/CarpetGreen"`
- `"AI2-THOR/Materials/Fabrics/CarpetWhite"`
- `"AI2-THOR/Materials/Fabrics/CarpetWhite 3"`
- `"AI2-THOR/Materials/Fabrics/HotelCarpet"` (red pattern)
- `"AI2-THOR/Materials/Fabrics/HotelCarpet3"` (red pattern)
- `"AI2-THOR/Materials/Fabrics/RUG2"` (red and blue pattern)
- `"AI2-THOR/Materials/Fabrics/Rug3"` (blue and red pattern)
- `"AI2-THOR/Materials/Fabrics/RUG4"` (red and yellow pattern)
- `"AI2-THOR/Materials/Fabrics/Rug5"` (white pattern)
- `"AI2-THOR/Materials/Fabrics/Rug6"` (green, purple, and red pattern)
- `"AI2-THOR/Materials/Fabrics/RUG7"` (red and blue pattern)
- `"AI2-THOR/Materials/Fabrics/RugPattern224"` (brown, green, and white pattern)
- `"Custom/Materials/AzureCarpetMCS"`
- `"Custom/Materials/BlueCarpetMCS"`
- `"Custom/Materials/ChartreuseCarpetMCS"`
- `"Custom/Materials/CyanCarpetMCS"`
- `"Custom/Materials/GreenCarpetMCS"`
- `"Custom/Materials/GreyCarpetMCS"`
- `"Custom/Materials/LimeCarpetMCS"`
- `"Custom/Materials/MagentaCarpetMCS"`
- `"Custom/Materials/MaroonCarpetMCS"`
- `"Custom/Materials/NavyCarpetMCS"`
- `"Custom/Materials/OliveCarpetMCS"`
- `"Custom/Materials/OrangeCarpetMCS"`
- `"Custom/Materials/PurpleCarpetMCS"`
- `"Custom/Materials/RedCarpetMCS"`
- `"Custom/Materials/RoseCarpetMCS"`
- `"Custom/Materials/SpringGreenCarpetMCS"`
- `"Custom/Materials/TealCarpetMCS"`
- `"Custom/Materials/VioletCarpetMCS"`
- `"Custom/Materials/WhiteCarpetMCS"`
- `"Custom/Materials/YellowCarpetMCS"`

Flat Materials
****************

Custom-made textures that are completely flat colors.

- `"Custom/Materials/Azure"`
- `"Custom/Materials/Black"`
- `"Custom/Materials/Blue"`
- `"Custom/Materials/Brown"`
- `"Custom/Materials/Chartreuse"`
- `"Custom/Materials/Cyan"`
- `"Custom/Materials/Goldenrod"`
- `"Custom/Materials/Green"`
- `"Custom/Materials/Grey"`
- `"Custom/Materials/Indigo"`
- `"Custom/Materials/Lime"`
- `"Custom/Materials/Magenta"`
- `"Custom/Materials/Maroon"`
- `"Custom/Materials/Navy"`
- `"Custom/Materials/Olive"`
- `"Custom/Materials/Orange"`
- `"Custom/Materials/Pink"`
- `"Custom/Materials/Purple"`
- `"Custom/Materials/Red"`
- `"Custom/Materials/Rose"`
- `"Custom/Materials/Silver"`
- `"Custom/Materials/SpringGreen"`
- `"Custom/Materials/Tan"`
- `"Custom/Materials/Teal"`
- `"Custom/Materials/Violet"`
- `"Custom/Materials/White"`
- `"Custom/Materials/Yellow"`

Metal Materials
***************

- `"AI2-THOR/Materials/Metals/BlackFoil"`
- `"AI2-THOR/Materials/Metals/BlackSmoothMeta"` (yes, it is misspelled)
- `"AI2-THOR/Materials/Metals/Brass 1"`
- `"AI2-THOR/Materials/Metals/Brass_Mat"`
- `"AI2-THOR/Materials/Metals/BrownMetal 1"`
- `"AI2-THOR/Materials/Metals/BrushedAluminum_Blue"`
- `"AI2-THOR/Materials/Metals/BrushedIron_AlbedoTransparency"`
- `"AI2-THOR/Materials/Metals/GenericStainlessSteel"`
- `"AI2-THOR/Materials/Metals/HammeredMetal_AlbedoTransparency 1"`
- `"AI2-THOR/Materials/Metals/Metal"`
- `"AI2-THOR/Materials/Metals/WhiteMetal"`
- `"UnityAssetStore/Baby_Room/Models/Materials/cabinet metal"`

Plastic Materials
*****************

- `"AI2-THOR/Materials/Plastics/BlackPlastic"`
- `"AI2-THOR/Materials/Plastics/OrangePlastic"`
- `"AI2-THOR/Materials/Plastics/WhitePlastic"`
- `"UnityAssetStore/Kindergarten_Interior/Models/Materials/color 1"` (flat red)
- `"UnityAssetStore/Kindergarten_Interior/Models/Materials/color 2"` (flat blue)
- `"UnityAssetStore/Kindergarten_Interior/Models/Materials/color 3"` (flat green)
- `"UnityAssetStore/Kindergarten_Interior/Models/Materials/color 4"` (flat yellow)

Rubber Materials
****************

- `"AI2-THOR/Materials/Plastics/BlueRubber"`
- `"AI2-THOR/Materials/Plastics/LightBlueRubber"`

Sofa 1 Materials
****************

Specific textures for `sofa_1` only.

- `"AI2-THOR/Materials/Fabrics/Sofa1_Blue"`
- `"AI2-THOR/Materials/Fabrics/Sofa1_Brown"`
- `"AI2-THOR/Materials/Fabrics/Sofa1_Red"`
- `"AI2-THOR/Materials/Fabrics/Sofa1_White"`

Sofa Chair 1 Materials
**********************

Specific textures for `sofa_chair_1` only.

- `"AI2-THOR/Materials/Fabrics/SofaChair1_Black"`
- `"AI2-THOR/Materials/Fabrics/SofaChair1_Blue"`
- `"AI2-THOR/Materials/Fabrics/SofaChair1_Brown"`
- `"AI2-THOR/Materials/Fabrics/SofaChair1_White"`

Sofa 2 Materials
****************

Specific textures for `sofa_2` AND `sofa_chair_2` only.

- `"AI2-THOR/Materials/Fabrics/SofaChair2_Grey"`
- `"AI2-THOR/Materials/Fabrics/SofaChair2_White"`
- `"AI2-THOR/Materials/Fabrics/SofaChair2_Fabric_AlbedoTransparency"`

Sofa 3 Materials
****************

Specific textures for `sofa_3` AND `sofa_chair_3` only.

- `"AI2-THOR/Materials/Fabrics/Sofa3_Blue"`
- `"AI2-THOR/Materials/Fabrics/Sofa3_Brown"`
- `"AI2-THOR/Materials/Fabrics/Sofa3_Green_Dark"`
- `"AI2-THOR/Materials/Fabrics/Sofa3_Red"`

Wall Materials
**************

- `"AI2-THOR/Materials/Walls/BrownDrywall"`
- `"AI2-THOR/Materials/Walls/Drywall"`
- `"AI2-THOR/Materials/Walls/DrywallBeige"`
- `"AI2-THOR/Materials/Walls/DrywallGreen"`
- `"AI2-THOR/Materials/Walls/DrywallOrange"`
- `"AI2-THOR/Materials/Walls/Drywall4Tiled"`
- `"AI2-THOR/Materials/Walls/EggshellDrywall"`
- `"AI2-THOR/Materials/Walls/RedDrywall"`
- `"AI2-THOR/Materials/Walls/WallDrywallGrey"`
- `"AI2-THOR/Materials/Walls/YellowDrywall"`
- `"Custom/Materials/AzureDrywallMCS"`
- `"Custom/Materials/BlueDrywallMCS"`
- `"Custom/Materials/ChartreuseDrywallMCS"`
- `"Custom/Materials/CyanDrywallMCS"`
- `"Custom/Materials/GreenDrywallMCS"`
- `"Custom/Materials/GreyDrywallMCS"`
- `"Custom/Materials/LimeDrywallMCS"`
- `"Custom/Materials/MagentaDrywallMCS"`
- `"Custom/Materials/MaroonDrywallMCS"`
- `"Custom/Materials/NavyDrywallMCS"`
- `"Custom/Materials/OliveDrywallMCS"`
- `"Custom/Materials/OrangeDrywallMCS"`
- `"Custom/Materials/PurpleDrywallMCS"`
- `"Custom/Materials/RedDrywallMCS"`
- `"Custom/Materials/RoseDrywallMCS"`
- `"Custom/Materials/SpringGreenDrywallMCS"`
- `"Custom/Materials/TealDrywallMCS"`
- `"Custom/Materials/VioletDrywallMCS"`
- `"Custom/Materials/WhiteDrywallMCS"`
- `"Custom/Materials/YellowDrywallMCS"`

Wood Materials
**************

- `"AI2-THOR/Materials/Wood/BlackWood"`
- `"AI2-THOR/Materials/Wood/BedroomFloor1"`
- `"AI2-THOR/Materials/Wood/DarkWood2"`
- `"AI2-THOR/Materials/Wood/DarkWoodSmooth2"`
- `"AI2-THOR/Materials/Wood/LightWoodCounters 1"`
- `"AI2-THOR/Materials/Wood/LightWoodCounters3"`
- `"AI2-THOR/Materials/Wood/LightWoodCounters4"`
- `"AI2-THOR/Materials/Wood/TexturesCom_WoodFine0050_1_seamless_S"`
- `"AI2-THOR/Materials/Wood/WhiteWood"`
- `"AI2-THOR/Materials/Wood/WoodFloorsCross"`
- `"AI2-THOR/Materials/Wood/WoodGrain_Brown"`
- `"AI2-THOR/Materials/Wood/WoodGrain_Tan"`
- `"AI2-THOR/Materials/Wood/WornWood"`
- `"Custom/Materials/AzureWoodMCS"`
- `"Custom/Materials/BlueWoodMCS"`
- `"Custom/Materials/ChartreuseWoodMCS"`
- `"Custom/Materials/CyanWoodMCS"`
- `"Custom/Materials/GreenWoodMCS"`
- `"Custom/Materials/GreyWoodMCS"`
- `"Custom/Materials/LimeWoodMCS"`
- `"Custom/Materials/MagentaWoodMCS"`
- `"Custom/Materials/MaroonWoodMCS"`
- `"Custom/Materials/NavyWoodMCS"`
- `"Custom/Materials/OliveWoodMCS"`
- `"Custom/Materials/OrangeWoodMCS"`
- `"Custom/Materials/PurpleWoodMCS"`
- `"Custom/Materials/RedWoodMCS"`
- `"Custom/Materials/RoseWoodMCS"`
- `"Custom/Materials/SpringGreenWoodMCS"`
- `"Custom/Materials/TealWoodMCS"`
- `"Custom/Materials/VioletWoodMCS"`
- `"Custom/Materials/WhiteWoodMCS"`
- `"Custom/Materials/YellowWoodMCS"`
- `"UnityAssetStore/Baby_Room/Models/Materials/wood 1"`
- `"UnityAssetStore/Kindergarten_Interior/Models/Materials/color wood 1"` (blue)
- `"UnityAssetStore/Kindergarten_Interior/Models/Materials/color wood 2"` (red)
- `"UnityAssetStore/Kindergarten_Interior/Models/Materials/color wood 3"` (green)
- `"UnityAssetStore/Kindergarten_Interior/Models/Materials/color wood 4"` (yellow)

