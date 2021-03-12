# Adding 3D Models

Here are the steps to add your own 3D models into the MCS simulation environment.

1. Download and open our Unity project (MCS fork of AI2-THOR) in the Unity Editor
2. Import your 3D models into our Unity project as Unity Prefab objects
3. Update your Unity Prefab objects with the correct AI2-THOR Unity scripts and subcomponents to work properly in the simulation environment
4. Update the MCS object registry file with references to your new objects
5. Manually test and verify that interaction with your new objects works as expected
6. Build a new version of the Unity project containing your additions
7. Update the Scene Generator with properties for your new objects
8. Optionally, submit a Pull Request to contribute your new objects to our public project

## Limitations

- Currently, our simulation environment does not support soft-body physics objects like blankets or stuffed animals.
- We have not tried using animations, audio, or fluids yet, so we cannot guarantee their performance.
- Successfully integrating existing objects that are part of the original AI2-THOR project but not yet available in the MCS simulation environment may necessitate making MCS-specific adjustments to those objects.
- This is a manually-intensive procedure that requires using the Unity Editor. Since human perception is needed for indentifying the correct pixels to position bounding boxes around and/or inside specific parts of the 3D model, we're not currently planning on making this procedure automated or dynamic. This is exactly how the MCS Core Team adds models into the simulation environment -- we have no secret shortcuts here.

## 1. Download and Open MCS in the Unity Editor

Clone the [MCS fork of AI2-THOR](https://github.com/NextCenturyCorporation/ai2thor) and follow the project's [setup instructions](https://github.com/NextCenturyCorporation/ai2thor#setup) to download and install the correct version of the Unity Editor and use it to load the MCS Unity project.

## 2. Import Your Models into Unity and Save Them as Prefabs

(Continuing from Step 1)

2A. Copy your 3D model into the `/unity/Assets/Resources/MCS/` folder (you can make a new subfolder for your models if you prefer).

2B. Navigate to the folder containing your model using the Project window of the Unity Editor. You should see your model there as a thumbnail.

2C. Click and drag your model's thumbnail into the Scene window. Your model should appear in the empty scene, and the name of your model's name should appear in the list in the Hierarchy window.

2D. Click and drag your model's name from the list in the Hierarchy window into your folder in the Project window. You should see a "Create Prefab" popup appear. Click the "Original Prefab" button to create a Unity Prefab file (".prefab") for your model. Please see the Unity Manual for more information about Prefabs.

## 3. Update Your Prefabs in Unity

(Continuing from Step 2)

3A. In the Hierarchy window, your model's name in the list is an instantiation of the Prefab, called a Game Object. Next to the Game Object, click the right arrow (`>`) on the right side of the list to edit the Prefab. This will change the Scene window to show a Prefab editing view. The Hierarchy window will now show just the Game Object. Depending on how your model was made, it may have one or more child Game Objects, shown as a nested view. Objects with multiple interactable parts (like, cabinet doors, drawers, and shelves) should have a child for each part. We'll call the parent Game Object the Target. In the Hierarchy window, click on the Target and look at the Inspector window to verify that it has a MeshFilter, MeshRenderer, and material(s); if it doesn't, then one of its children should have them (click on each child in turn).

3B. Ideally, the Target should always be centered on the X/Z axis. First, in the Hierarchy window, click on the Target; then, in the Inspector window, in the Transform Component, zero out its Position. If the Target still isn't centered, then the 3D model itself may be off-center: adjust the Position in the Target's Transform Component to visually center the object on the X/Z axis. Failing to do this may cause the Scene Generator to generate buggy scenes containing clipping objects.

3C. Click on the Target. In the Inspector window, set the Tag to "SimObjPhysics" and the Layer to "SimObjVisible". Click on the Add Component button to add a Rigidbody Component to the Target. Ensure its "Use Gravity" is set to true.

3D. In the Inspector window, review the Target's existing Unity Components (the separate dropdown sections). If the Target (or any of its children) doesn't have a Collider Component, you'll have to add some. Please see the Unity Manual for more information about Colliders.

- In the Hierarchy window, right-click on the Target and create an Empty Child.
- In the Inspector window, rename it to "Colliders" and mark it Static.
- Right-click on the "Colliders" Game Object and create an Empty Child for each Collider you need to have.
- On each "Colliders" child, in the Inspector window:
  - Rename it to a useful name.
  - Add a Collider Component (normally a box, but sometimes others -- note that all MeshColliders should be CONVEX).
  - Adjust the Transform Component and/or Collider Component to visually position, rotate, and scale the Collider to the appropriate pixels.
  - Set the Tag to "SimObjPhysics" and the Layer to "SimObjVisible".

3E. Next you must add "Visibility Points" along the visible pixel boundaries of your model. AI2-THOR raycasts from the performer agent to an object's Visibility Points in order to determine if the object is visible (and can be an action target). The greater number of Visibility Points, the more accurate the visibility readings will be. Our suggestion is to position one Visibility Point at each of the object's corners, plus one or more in a grid along each of the object's 6 sides.

- In the Hierarchy window, right-click on the Target and create an Empty Child.
- In the Inspector window, rename it to "VisibilityPoints" (no space!) and mark it Static.
- Right-click on the "VisibilityPoints" Game Object and create an Empty Child for each Visibility Point you want to have.
- On each Visibility Point Game Object, in the Inspector window:
  - Adjust the Transform Component to visually position the Visibility Point to the appropriate pixels. (To see the Visibility Point's position in the Scene window, you can set a colored Icon on the Visibility Point Game Object using the cube button in the top-left corner of the Inspector window.)
  - Set the Layer to "SimObjVisible".

3F. Next you must add a single "Bounding Box" containing the whole 3D model. You cannot reuse an existing Collider for this.

- In the Hierarchy window, right-click on the Target and create an Empty Child.
- In the Inspector window, rename it to "BoundingBox" (no space!) and set its Layer to "SimObjInvisible".
- Click on the Add Component button to add a BoxCollider Component.
- In the BoxCollider Component, click the checkbox to mark it as NOT ACTIVE.
- Adjust the Transform Component (but not the BoxCollider Component -- adjusting both makes it harder on us later) to visually position, rotate, and scale the Collider to the appropriate pixels completely enclosing the model. Take note of the position, rotation, and scale for step 7 later.

3G. Next you must add a SimObjPhysics Component to the Target. This AI2-THOR Script enables interaction with the object.

- In the Hierarchy window, click on the Target.
- In the Inspector window, click on the Add Component button to add a SimObjPhysics Component.
- In the SimObjPhysics (Script) Component:
  - Set the "Primary Property" to "Static" (for non-moveable objects), "Moveable", or "Can Pickup" (a subset of Moveable).
  - Set the "Secondary Properties" as needed (we use: "Receptacle" for objects on which you can use the PutObject action; "Can Open" for openable objects; "Stacking" for blocks). You will need to adjust the size of the "Secondary Properties" array before you can add new elements to it.
  - Set the "Bounding Box" property to the "BoundingBox" Game Object that you made.
  - Set the "Visibility Points" array property to have each Visibility Point Game Object that you made. This is easy if you right-click on the Inspector tab, click "Lock", go to the Hierarcy window, use click-shift-click to select all Visibility Points simultaneously, and click-and-drag them over from the Hierarchy window onto the "Visibility Points" label in the SimObjPhysics (Script) Component.
  - Set the "My Colliders" array property to have each Collider Game Object that you made.
  - Optionally, set the "Salient Materials" property as needed.

3H. If the Target is openable, like a cabinet or drawer, you must add a "Can Open_Object" Component to the Target. This AI2-THOR Script enables opening and closing the object and adjusting its visual appearance.

- In the Hierarchy window, click on the Target.
- In the Inspector window, click on the Add Component button to add a "Can Open_Object" Component.
- In the "Can Open_Object" (Script) Component:
  - Set the "Moving Parts" property to the Target.
  - Adjust the "Open Positions" and "Close Positions" to visually position, rotate, or scale the model to the approriate pixels for its "opened" and "closed" positions respectfully. Change the "Movement Type" property to "Slide", "Rotate", or "Scale" as needed, depending on how the model should change when it's opened.

3I. If the Target is a Receptacle (you want to enable the use of the PutObject action to place held objects on top of your Target):

- In the Hierarchy window, right-click on the Target and create an Empty Child.
- In the Inspector window, rename it to "ReceptacleTriggerBox" (no space!) and mark it Static.
- Set the Tag to "Receptacle" and the Layer to "SimObjInvisible".
- Click on the Add Component button to add a BoxCollider Component.
- In the BoxCollider Component, set the "Is Trigger" property to true.
- Adjust the Transform Component (but not the BoxCollider Component -- adjusting both makes it harder on us later) to visually position, rotate, and scale the Collider to the appropriate pixels completely enclosing the receptacle area on which held objects may be placed. (I'm not sure if the height actually matters).
- Click on the Add Component button to add a Contains Component.

3J. For each distinct interactable part within the Target (like cabinet doors, drawers, and shelves):

- Right-click on the Target and create an Empty Child (we'll call this the Sub-Target).
- Rename the Sub-Target to a useful name.
- In the Hierarchy window, click-and-drag to move the Game Object containing the MeshFilter and MeshRenderer Components corresponding to the Sub-Target under the Sub-Target.
- Repeat steps 3C-3J (EXCEPT 3F) on the Sub-Target.

3K. In the Hierarchy window, click the left arrow (`<`) in the top-left corner to save your Prefab and exit the editing view.

## 4. Update the Object Registry File

In the MCS fork of AI2-THOR, in `/unity/Assets/Resources/MCS/mcs_object_registry.json`, add a new entry for your object that contains the following properties:

- `id` (string): The object's unique ID which will correspond to the `type` property in MCS JSON scene files. Please ensure that you don't use an ID/type that's already taken (see our [SCHEMA doc](https://github.com/NextCenturyCorporation/MCS/blob/master/machine_common_sense/scenes/SCHEMA.md#object-list) for the full list).
- `resourceFile` (string): The path to the object's Prefab file, starting in the `/unity/Assets/Resources/MCS/` folder, and WITHOUT the `.prefab` extension. Examples:
  - If your Prefab file is `/unity/Assets/Resources/MCS/thing.prefab`, your `resourceFile` property should be `thing`
  - If your Prefab file is `/unity/Assets/Resources/MCS/subfolder/thing.prefab`, your `resourceFile` property should be `subfolder/thing`
- `shape` (string): The object's human-readable shape that's returned in the Python output metadata.

You can also add other properties to entries in the JSON object registry file. Most object properties supported in scene files (like `moveable` or `pickupable`) are also supported in the object registry. Any properties defined for an object in the object registry file are applied to all instances of that object in all scenes. Please let us know if you'd like us to make some documentation on the available properties.

## 5. Manually Test and Verify Your Objects

5A. TODO

## 6. Build Unity

Inside the Unity Editor, go to `File->Build Settings` to open the Build Settings popup window, then build the project by selecting your Target Platform and clicking the Build button.

## 7. Update the Scene Generator

If you want to have your new models appear in the random scenes made by our [Scene Generator](https://github.com/NextCenturyCorporation/mcs-scene-generator), you must add some information about the models into the Scene Generator's source code.

7A. TODO

## 8. Submit a Pull Request

Optionally, if you would like to contribute your objects to the public MCS simulation environment (in our GitHub source code repository) for other teams to use, and have legal permission to share your models, then you may submit a Pull Request to the MCS fork of AI2-THOR containing your new Prefabs and updates to the object registry file.

## Troubleshooting

If you have any questions about the procedure, please contact the MCS Core Team via a GitHub Issue, the MCS Slack, or email: mcs-ta2@machinecommonsense.com
