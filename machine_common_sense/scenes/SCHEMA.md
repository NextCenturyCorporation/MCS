# MCS Scene Configuration Files: API

- [Scenes](#scenes)
  - [Scene Config](#scene-config)
  - [Object Config](#object-config)
  - [Goal Config](#goal-config)
  - [Goal Metadata Config](#goal-metadata-config)
  - [Answer Config](#answer-config)
  - [Move Config](#move-config)
  - [Physics Config](#physics-config)
  - [Show Config](#show-config)
  - [Size Config](#size-config)
  - [Single Step Config](#single-step-config)
  - [Step Begin and End Config](#step-begin-and-end-config)
  - [Teleport Config](#teleport-config)
  - [Transform Config](#transform-config)
  - [Vector Config](#vector-config)
- [Object List](#object-list)
- [Material List](#material-list)

## Scenes

A **scene** is a JSON object (called a [scene config](#scene-config)) that, when passed to the MCS Unity application via the MCS Python Library, describes the objects, materials (colors and textures), and scripted actions that will happen in that specific instance of the MCS 3D simulation environment.

Please note that all scenes are currently in a room that is 5-by-5 (X/Z) and 3 high (Y) using Unity's global coordinate system, where we consider 1 unit to be approximately 2 feet.

### Scene Config

Example:

```json
{
    "name": "Example MCS Scene Configuration",
    "verison": 2,
    "ceilingMaterial": "AI2-THOR/Materials/Walls/Drywall",
    "floorMaterial": "AI2-THOR/Materials/Fabrics/CarpetWhite 3",
    "wallMaterial": "AI2-THOR/Materials/Walls/DrywallBeige",
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
```

Each **scene config** has the following properties:


- `answer` ([answer config](#answer-config), optional): The best answer to the goal for the scene. Default: none
- `ceilingMaterial` (string, optional): The material (color/texture) for the room's ceiling. See the [Material List](#material-list) for options. Default (v0.0.3+): `"AI2-THOR/Materials/Walls/Drywall"`
- `floorMaterial` (string, optional): The material (color/texture) for the room's floor. See the [Material List](#material-list) for options. Default (v0.0.3+): `"AI2-THOR/Materials/Fabrics/CarpetWhite 3"`
- `floorProperties` ([physics config](#physics-config), optional): Enable custom friction, bounciness, and/or drag on the floor. Default: see [physics config](#physics-config).
- `goal` ([goal config](#goal-config), optional): The goal for the scene. Default: none
- `intuitivePhysics` (bool, optional): Specific performer and room setup for intuitive physics scenes.
- `isometric` (bool, optional): Specific performer and room setup for agent scenes.
- `name` (string, optional): A unique name for the scene used for our logs. Default: the filename
- `objects` ([object config](#object-config) array, optional): The objects for the scene. Default: `[]`
- `performerStart` ([transform config](#transform-config), optional): The starting position and rotation of the performer (the "player"). Only the `position.x`, `position.z`, `rotation.x` (head tilt), and `rotation.y` properties are used. Default: `{ "position": { "x": 0, "z": 0 }, "rotation": { "y": 0 } }`
- `version` (int, optional): The version of this scene configuration. Default: the latest version
- `wallMaterial` (string, optional): The material (color/texture) for the room's four outer walls. See the [Material List](#material-list) for options. Default (v0.0.3+): `"AI2-THOR/Materials/Walls/DrywallBeige"`
- `wallProperties` ([physics config](#physics-config), optional): Enable custom friction, bounciness, and/or drag on the walls. Default: see [physics config](#physics-config).

### Object Config

Each **object config** has the following properties:

- `id` (string, required): The object's unique ID.
- `type` (string, required): The object's type from the [Object List](#object-list).
- `forces` ([move config](#move-config) array, optional): The steps on which to apply [force](https://docs.unity3d.com/ScriptReference/Rigidbody.AddForce.html) to the object. The config `vector` describes the amount of force (in Newtons) to apply in each direction using the global coordinate system. Resets all existing forces on the object to 0 before applying the new force. Default: `[]`
- `hides` ([single step config](#single-step-config) array, optional): The steps on which to hide the object, completely removing its existence from the scene until it is shown again (see the `shows` property). Useful if you want to have impossible events (spontaneous disappearance). Default: `[]`
- `kinematic` (boolean, optional): If true, the object will ignore all forces including gravity. See Unity's [isKinematic property](https://docs.unity3d.com/ScriptReference/Rigidbody-isKinematic.html). Usually paired with `structure`. Default: `false`
- `locationParent` (string, optional): The `id` of another object in the scene. If given, this object's `shows.position` and `shows.rotation` will both start from the position and rotation of the `locationParent` object rather than from `0`. Default: none
- `mass` (float, optional): The mass of the object, which affects the physics simulation. Default: `1`
- `materials` (string array, optional): The material(s) (colors/textures) of the object. An object `type` may use multiple individual materials; if so, they must be listed in a specific order. Please note that most non-primitive objects already have specific material(s). See the [Material List](#material-list) for options. Default: none
- `materialFile` (string, optional): Deprecated (please use `materials` now). The material (color/texture) of the object. Please note that most non-primitive objects already have specific material(s). See the [Material List](#material-list) for options. Default: none
- `moveable` (boolean, optional): Whether the object should be moveable, if it is not already moveable based on its `type`. Default: depends on `type`
- `moves` ([move config](#move-config) array, optional): The steps on which to move the object, moving it from one position in the scene to another. The config `vector` describes the amount of position to change, added to the object's current position. Useful if you want to move objects that are `kinematic`. A fifth of each move is made over each of the five substeps (five screenshots) during the step. Default: `[]`
- `nullParent` ([transform config](#transform-config), optional): Whether to wrap the object in a null parent object. Useful if you want to rotate an object by a point other than its center point. Default: none
- `openable` (boolean, optional): Whether the object should be openable, if it is not already openable based on its `type`. Default: depends on `type`
- `opened` (boolean, optional): Whether the object should begin opened. Must also be `openable`. Default: `false`
- `physicsProperties` ([physics config](#physics-config), optional): Enable custom friction, bounciness, and/or drag on the object. Default: see [physics config](#physics-config).
- `pickupable` (boolean, optional): Whether the object should be pickupable, if it is not already openable based on its `type`. Pickupable objects are also automatically `moveable`. Default: depends on `type`
- `resizes` ([size config](#size-config) array, optional): The steps on which to resize the object. The config `size` is multiplied by the object's current size. Useful if you want to have impossible events (spontaneous resizing). Default: `[]`
- `rotates` ([move config](#move-config) array, optional): The steps on which to rotate the object. The config `vector` describes the amount of rotation (in degrees) to change, added to the object's current rotation. Useful if you want to rotate objects that are `kinematic`. A fifth of each move is made over each of the five substeps (five screenshots) during the step. Default: `[]`
- `salientMaterials` (string array, optional)
- `shows` ([show config](#show-config) array, optional): The steps on which to show the object, adding its existence to the scene. Please note that each object begins hidden within the scene, so each object should have at least one element in its `shows` array to be useful. Default: `[]`
- `shrouds` ([step being and end config config](#step-begin-and-end-config) array, optional): The steps on which to shroud the object, temporarily making it invisible, but moving with its existing intertia and able to collide with objects. Useful if you want to have impossible events. Default: `[]`
- `structure` (boolean, optional): Whether the object is a structural part of the environment. Usually paired with `kinematic`. Default: `false`
- `teleports` ([teleport config](#teleport-config) array, optional): The steps on which to teleport the object, teleporting it from one position in the scene to another. The config `position` describes the object's end position in global coordinates and is not affected by the object's current position. Useful if you want to have impossible events (spontaneous teleportation). Default: `[]`
- `torques` ([move config](#move-config) array, optional): The steps on which to apply [torque](https://docs.unity3d.com/ScriptReference/Rigidbody.AddTorque.html) to the object. The config `vector` describes the amount of torque (in Newtons) to apply in each direction using the global coordinate system. Resets all existing torques on the object to 0 before applying the new torque. Default: `[]`

### Goal Config

Each **goal config** has the following properties:

- `action_list` (string array array, optional): The list of actions that are available for the scene at each step (outer list index).  Each inner list item is a list of action strings. For example, `['MoveAhead','RotateLook,rotation=180']` restricts the actions to either `'MoveAhead'` or `'RotateLook'` with the `'rotation'` parameter set to `180`. An empty outer `action_list` means that all actions are always available. An empty inner list means that all actions are available for that specific step. Default: none
- `info_list` (array, optional): A list of information for the visualization interface associated with this goal. Default: none
- `last_preview_phase_step` (integer, optional): The last step of the preview phase of this scene, if any. Default: -1
- `last_step` (integer, optional): The last step of this scene. This scene will automatically end following this step.
- `metadata` ([goal metadata config](#goal-metadata-config), optional): The metadata specific to this goal. Default: none
- `task_list` (string array, optional): A list of types for the visualization interface associated with this goal, including the relevant MCS core domains. Default: none
- `type_list` (string array, optional) A list of tasks for the visualization interface associated with this goal (secondary to its types).

### Goal Metadata Config

Each **goal metadata config** has the following properties:

(Coming soon!)

### Answer Config

Each **answer config** has the following properties:

(Coming soon!)

### Move Config

Each **move config** has the following properties:

- `stepBegin` (integer, required): The step on which the action should begin.  Must be non-negative.  A value of `0` means the action will begin during scene initialization.
- `stepEnd` (integer, required): The step on which the action should end.  Must be equal to or greater than the `stepBegin`.
- `vector` ([vector config](#vector-config), required): The coordinates to describe the movement. Default: `{ "x": 0, "y": 0, "z": 0 }`

### Physics Config

Each **physics config** has the following properties:

- `enable` (bool, optional): Whether to enable customizing ALL physics properties on the object. You must either customize no properties or all of them. Any unset property in this config will automatically be set to `0`, NOT its Unity default (see below). Default: `false`
- `angularDrag` (float, optional): The object's [angular drag](https://docs.unity3d.com/ScriptReference/Rigidbody-angularDrag.html), between 0 and 1. Default: `0`
- `bounciness` (float, optional): The object's [bounciness](https://docs.unity3d.com/ScriptReference/PhysicMaterial-bounciness.html), between 0 and 1. Default: `0`
- `drag` (float, optional): The object's [drag](https://docs.unity3d.com/ScriptReference/Rigidbody-drag.html). Default: `0`
- `dynamicFriction` (float, optional): The object's [dynamic friction](https://docs.unity3d.com/ScriptReference/PhysicMaterial-dynamicFriction.html), between 0 and 1. Default: `0`
- `staticFriction` (float, optional): The object's [static friction](https://docs.unity3d.com/ScriptReference/PhysicMaterial-staticFriction.html), between 0 and 1. Default: `0`

If no physics config is set, or if the physics config is not enabled, the object will have the following Unity defaults:

- Angular Drag: `0.5`
- Bounciness: `0`
- Drag: `0`
- Dynamic Friction: `0.6`
- Static Friction: `0.6`

### Show Config

Each **show config** has the following properties:

- `stepBegin` (integer, required): The step on which to show the object.  Must be non-negative.  A value of `0` means the object will be shown during scene initialization.
- `position` ([vector config](#vector-config), optional): The object's position within the environment using the global coordinate system. Default: `{ "x": 0, "y": 0, "z": 0 }`
- `rotation` ([vector config](#vector-config), optional): The object's rotation (in degrees) within the environment using the global coordinate system. Default: `{ "x": 0, "y": 0, "z": 0 }`
- `scale` ([vector config](#vector-config), optional): The object's scale, which is multiplied by its base scale. Default: `{ "x": 1, "y": 1, "z": 1 }`

### Size Config

Each **size config** has the following properties:

- `stepBegin` (integer, required): The step on which the action should begin.  Must be non-negative.  A value of `0` means the action will begin during scene initialization.
- `stepEnd` (integer, required): The step on which the action should end.  Must be equal to or greater than the `stepBegin`.
- `size` ([vector config](#vector-config), required): The coordinates to describe the size, which is multiplied by the object's current size. Default: `{ "x": 1, "y": 1, "z": 1 }`

### Single Step Config

Each **single step config** has the following properties:

- `stepBegin` (integer, required): The step on which the action should occur.  Must be non-negative.  A value of `0` means the action will occur during scene initialization.

### Step Begin and End Config

Each **step begin and end config** has the following properties:

- `stepBegin` (integer, required): The step on which the action should occur.  Must be non-negative.  A value of `0` means the action will occur during scene initialization.
- `stepEnd` (integer, required): The step on which the action should end.  Must be equal to or greater than the `stepBegin`.

### Teleport Config

Each **teleport config** has the following properties:

- `stepBegin` (integer, required): The step on which the action should begin.  Must be non-negative.  A value of `0` means the action will begin during scene initialization.
- `position` ([vector config](#vector-config), required): The global coordinates to describe the end position. Default: `{ "x": 0, "y": 0, "z": 0 }`

### Transform Config

Each **transform config** has the following properties:

- `position` ([vector config](#vector-config), optional): The object's position within the environment using the global coordinate system. Default: `{ "x": 0, "y": 0, "z": 0 }`
- `rotation` ([vector config](#vector-config), optional): The object's rotation (in degrees) within the environment using the global coordinate system. Default: `{ "x": 0, "y": 0, "z": 0 }`
- `scale` ([vector config](#vector-config), optional): The object's scale, which is multiplied by its base scale.  Default: `{ "x": 1, "y": 1, "z": 1 }`

### Vector Config

Each **vector config** has the following properties:

- `x` (float, optional)
- `y` (float, optional)
- `z` (float, optional)

## Object List

### Attributes

- Moveable: Can be pushed, pulled, and knocked over. Can be added to object types that are not `moveable` by default.
- Pickupable: Can be picked up with the `PickupObject` action (all pickupable objects are also moveable). Can be added to object types that are not `pickupable` by default.
- Receptacle: Can hold objects with the `PutObject` action.
- Openable: Can be opened with the `OpenObject` action.

You can use any of these strings with an object's `type` property.

### Block Objects (Blank)

Blocks have the `pickupable` and `receptacle` attributes by default. Use the [block materials (blank)](#block-materials-blank).

| Object Type | Shape | Default Mass |
| --- | --- | --- |
| `"block_blank_blue_cube"` | blank block cube | 0.66 |
| `"block_blank_blue_cylinder"` | blank block cylinder | 0.66 |
| `"block_blank_red_cube"` | blank block cube | 0.66 |
| `"block_blank_red_cylinder"` | blank block cylinder | 0.66 |
| `"block_blank_wood_cube"` | blank block cube | 0.66 |
| `"block_blank_wood_cylinder"` | blank block cylinder | 0.66 |
| `"block_blank_yellow_cube"` | blank block cube | 0.66 |
| `"block_blank_yellow_cylinder"` | blank block cylinder | 0.66 |

### Block Objects (Letter/Number)

Blocks have the `pickupable` and `receptacle` attributes by default. Use the [block materials (letter/number)](#block-materials-letter-number).

| Object Type | Shape | Default Mass |
| --- | --- | --- |
| `"block_blue_letter_a"` | letter block cube | 0.66 |
| `"block_blue_letter_b"` | letter block cube | 0.66 |
| `"block_blue_letter_c"` | letter block cube | 0.66 |
| `"block_blue_letter_d"` | letter block cube | 0.66 |
| `"block_blue_letter_m"` | letter block cube | 0.66 |
| `"block_blue_letter_s"` | letter block cube | 0.66 |
| `"block_yellow_number_1"` | number block cube | 0.66 |
| `"block_yellow_number_2"` | number block cube | 0.66 |
| `"block_yellow_number_3"` | number block cube | 0.66 |
| `"block_yellow_number_4"` | number block cube | 0.66 |
| `"block_yellow_number_5"` | number block cube | 0.66 |
| `"block_yellow_number_6"` | number block cube | 0.66 |

### Pickupable Objects

The following object types have the `pickupable` attribute by default.

| Object Type | Shape | Default Mass | Receptacle | Openable | Materials |
| --- | --- | --- | --- | --- | --- |
| `"apple_1"` | apple | 0.25 | | | none |
| `"apple_2"` | apple | 0.25 | | | none |
| `"ball"` | ball | 1 | | | block (blank), metal, plastic, rubber, wood |
| `"cake"` | cake | 0.5 | | | none |
| `"car_1"` | car | 0.5 | | | block (blank), wood |
| `"crayon_black"` | crayon | 0.125 | | | none |
| `"crayon_blue"` | crayon | 0.125 | | | none |
| `"crayon_green"` | crayon | 0.125 | | | none |
| `"crayon_pink"` | crayon | 0.125 | | | none |
| `"crayon_red"` | crayon | 0.125 | | | none |
| `"crayon_yellow"` | crayon | 0.125 | | | none |
| `"duck_on_wheels"` | duck | 0.5 | | | block (blank), wood |
| `"bowl_3"` | bowl | 0.25 | X | | metal, plastic, wood |
| `"bowl_4"` | bowl | 0.25 | X | | metal, plastic, wood |
| `"bowl_6"` | bowl | 0.25 | X | | metal, plastic, wood |
| `"cup_2"` | cup | 0.25 | X | | metal, plastic, wood |
| `"cup_3"` | cup | 0.25 | X | | metal, plastic, wood |
| `"cup_6"` | cup | 0.25 | X | | metal, plastic, wood |
| `"gift_box_1"` | box | 0.5 | X | X | cardboard |
| `"trophy"` | trophy | 0.5 | | | none |
| `"pacifier"` | pacifier | | 0.5 | | none |
| `"plate_1"` | plate | 0.25 | X | | metal, plastic, wood |
| `"plate_3"` | plate | 0.25 | X | | metal, plastic, wood |
| `"plate_4"` | plate | 0.25 | X | | metal, plastic, wood |
| `"racecar_red"` | car | 0.5 | | | block (blank), wood |
| `"suitcase_1"` | box | 5 | X | X | metal, plastic |
| `"turtle_on_wheels"` | turtle | | | 0.5 | block (blank), wood |

### Furniture Objects

| Object Type | Shape | Default Mass | Moveable | Receptacle | Openable | Materials | Details |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `"chest_1"` | box | 15 | | X | X | metal, plastic, wood | Rectangular box |
| `"chest_2"` | box | 15 | | X | X | metal, plastic, wood | Treasure chest |
| `"chair_1"` | chair | 5 | X | X | | metal, plastic, wood | |
| `"chair_2"` | stool | 2.5 | X | X | | metal, plastic, wood | |
| `"changing_table"` | changing table | 100 | | X | X | wood | |
| `"crib"` | crib | 25 | | | | wood | |
| `"foam_floor_tiles"` | foam floor tiles | 1 | | | | none | |
| `"shelf_1"` | shelf | 10 | | X | | metal, plastic, wood | Object with four cubbies | |
| `"shelf_2"` | shelf | 20 | | X | | metal, plastic, wood | Object with three shelves | |
| `"sofa_1"` | sofa | 100 | | X | | sofa 1 | |
| `"sofa_2"` | sofa | 100 | | X | | sofa 2 | |
| `"sofa_chair_1"` | sofa chair | 50 | | X | | sofa chair 1 | |
| `"sofa_chair_2"` | sofa chair | 50 | | X | | sofa 2 | |
| `"table_1"` | table | 10 | X | X | | metal, plastic, wood | Rectangular table with legs | |
| `"table_3"` | table | 2.5 | X | X | | metal, plastic, wood | Circular table | |
| `"table_5"` | table | 20 | X | X | | metal, plastic, wood | Rectangular table with sides | |
| `"wardrobe"` | wardrobe | 100 | | X | X | wood | |

### Primitive Objects

The following primitive shapes have the `pickupable` attribute by default, a default mass of 1, default dimensions of (x=1, y=1, z=1), and no material restrictions. Please note these are NOT the internal Unity primitive 3D GameObjects.

- `"cone"`
- `"cube"`
- `"cylinder"`
- `"sphere"`
- `"square_frustum"`

### Deprecated Objects

The following object types are not currently used:

| Object Type | Moveable | Pickupable | Receptacle | Openable | Materials |
| --- | --- | --- | --- | --- | --- |
| `"box_2"` | X | X | X | X | cardboard |
| `"box_3"` | X | X | X | X | cardboard |
| `"box_4"` | X | X | X | X | cardboard |
| `"painting_2"` | | | | | none |
| `"painting_4"` | | | | | none |
| `"painting_5"` | | | | | none |
| `"painting_9"` | | | | | none |
| `"painting_10"` | | | | | none |
| `"painting_16"` | | | | | none |
| `"plant_1"` | | | | | none |
| `"plant_5"` | | | | | none |
| `"plant_7"` | | | | | none |
| `"plant_9"` | | | | | none |
| `"plant_12"` | | | | | none |
| `"plant_16"` | | | | | none |

### Child Components

Some objects have child components representing cabinets, drawers, or shelves. Child components are not found in the scene configuration file but are automatically generated by the MCS environment. Child components have their own object IDs so the player may use actions like OpenObject or PutObject with specific cabinets/drawers/shelves.

The following objects have the following child components:

- `"changing_table"`:
  - `"<id>_drawer_top"`
  - `"<id>_drawer_bottom"`
  - `"<id>_shelf_top"`
  - `"<id>_shelf_middle"`
  - `"<id>_shelf_bottom"`

## Material List

In Unity, "Materials" are the colors and textures applied to objects in the 3D simulation environment. Some objects may have default materials. Some objects may have multiple materials. Some materials may have patterns intended for objects of a specific size, and may look odd if applied to objects that are too big or small.

For our training and evaluation datasets, we normally use the materials under "Walls", "Ceramics", "Fabrics", and "Woods" for the ceiling and the walls, and the materials under "Ceramics", "Fabrics", and "Woods" for the floors.

The following materials are currently available:

### Block Materials (Blank)

Colors that look good on the blank blocks, as well as some of the baby toys.

- `"UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/blue_1x1"`
- `"UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/gray_1x1"`
- `"UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/green_1x1"`
- `"UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/red_1x1"`
- `"UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/wood_1x1"`
- `"UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/yellow_1x1"`

### Block Materials (Letter/Number)

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

### Cardboard Materials

- `"AI2-THOR/Materials/Misc/Cardboard_Brown"`
- `"AI2-THOR/Materials/Misc/Cardboard_Grey"`
- `"AI2-THOR/Materials/Misc/Cardboard_Tan"`

### Ceramic Materials

- `"AI2-THOR/Materials/Ceramics/BrownMarbleFake 1"`
- `"AI2-THOR/Materials/Ceramics/ConcreteBoards1"`
- `"AI2-THOR/Materials/Ceramics/GREYGRANITE"`
- `"AI2-THOR/Materials/Ceramics/PinkConcrete_Bedroom1"`
- `"AI2-THOR/Materials/Ceramics/RedBrick"`
- `"AI2-THOR/Materials/Ceramics/TexturesCom_BrickRound0044_1_seamless_S"` (rough stone)
- `"AI2-THOR/Materials/Ceramics/WhiteCountertop"`

### Fabric Materials

- `"AI2-THOR/Materials/Fabrics/Carpet2"`
- `"AI2-THOR/Materials/Fabrics/Carpet4"`
- `"AI2-THOR/Materials/Fabrics/CarpetDark"`
- `"AI2-THOR/Materials/Fabrics/CarpetGreen"`
- `"AI2-THOR/Materials/Fabrics/CarpetWhite 3"`
- `"AI2-THOR/Materials/Fabrics/HotelCarpet3"` (red pattern)
- `"AI2-THOR/Materials/Fabrics/RugPattern224"` (brown, green, and white pattern)

### Metal Materials

- `"AI2-THOR/Materials/Metals/BlackFoil"`
- `"AI2-THOR/Materials/Metals/BlackSmoothMeta"` (yes, it is misspelled)
- `"AI2-THOR/Materials/Metals/Brass 1"`
- `"AI2-THOR/Materials/Metals/Brass_Mat"`
- `"AI2-THOR/Materials/Metals/BrownMetal 1"`
- `"AI2-THOR/Materials/Metals/BrushedIron_AlbedoTransparency"`
- `"AI2-THOR/Materials/Metals/GenericStainlessSteel"`
- `"AI2-THOR/Materials/Metals/HammeredMetal_AlbedoTransparency 1"`
- `"AI2-THOR/Materials/Metals/Metal"`
- `"AI2-THOR/Materials/Metals/WhiteMetal"`
- `"UnityAssetStore/Baby_Room/Models/Materials/cabinet metal"`

### Plastic Materials

- `"AI2-THOR/Materials/Plastics/BlackPlastic"`
- `"AI2-THOR/Materials/Plastics/OrangePlastic"`
- `"AI2-THOR/Materials/Plastics/WhitePlastic"`
- `"UnityAssetStore/Kindergarten_Interior/Models/Materials/color 1"` (flat red)
- `"UnityAssetStore/Kindergarten_Interior/Models/Materials/color 2"` (flat blue)
- `"UnityAssetStore/Kindergarten_Interior/Models/Materials/color 3"` (flat green)
- `"UnityAssetStore/Kindergarten_Interior/Models/Materials/color 4"` (flat yellow)

### Rubber Materials

- `"AI2-THOR/Materials/Plastics/BlueRubber"`
- `"AI2-THOR/Materials/Plastics/LightBlueRubber"`

### Sofa 1 Materials

Specific textures for `sofa_1` only.

- `"AI2-THOR/Materials/Fabrics/Sofa1_Brown"`
- `"AI2-THOR/Materials/Fabrics/Sofa1_Red"`

### Sofa Chair 1 Materials

Specific textures for `sofa_chair_1` only.

- `"AI2-THOR/Materials/Fabrics/SofaChair1_Black"`
- `"AI2-THOR/Materials/Fabrics/SofaChair1_Brown"`

### Sofa 2 Materials

Specific textures for `sofa_2` AND `sofa_chair_2` only.

- `"AI2-THOR/Materials/Fabrics/SofaChair2_Grey"`
- `"AI2-THOR/Materials/Fabrics/SofaChair2_White"`

### Wall Materials

- `"AI2-THOR/Materials/Walls/Drywall"`
- `"AI2-THOR/Materials/Walls/DrywallBeige"`
- `"AI2-THOR/Materials/Walls/DrywallGreen"`
- `"AI2-THOR/Materials/Walls/DrywallOrange"`
- `"AI2-THOR/Materials/Walls/Drywall4Tiled"`
- `"AI2-THOR/Materials/Walls/EggshellDrywall"`
- `"AI2-THOR/Materials/Walls/RedDrywall"`
- `"AI2-THOR/Materials/Walls/WallDrywallGrey"`
- `"AI2-THOR/Materials/Walls/YellowDrywall"`

### Wood Materials

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
- `"UnityAssetStore/Baby_Room/Models/Materials/wood 1"`
- `"UnityAssetStore/Kindergarten_Interior/Models/Materials/color wood 1"` (blue)
- `"UnityAssetStore/Kindergarten_Interior/Models/Materials/color wood 2"` (red)
- `"UnityAssetStore/Kindergarten_Interior/Models/Materials/color wood 3"` (green)
- `"UnityAssetStore/Kindergarten_Interior/Models/Materials/color wood 4"` (yellow)

