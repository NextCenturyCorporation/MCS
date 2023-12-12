# Task List

Table of Content:
- [Interactive Tasks](#interactive-tasks)
  - [Overview](#interactive-overview)
  - [Data](#interactive-data)
  - [Introduced in Evaluation 3](#interactive-tasks-introduced-in-evaluation-3)
    - [Retrieval - Containers](#retrieval---containers)
    - [Retrieval - Obstacles](#retrieval---obstacles)
    - [Retrieval - Occluders](#retrieval---occluders)
  - [Introduced in Evaluation 4](#interactive-tasks-introduced-in-evaluation-4)
    - [Object Permanence (Interactive)](#object-permanence-interactive)
  - [Introduced in Evaluation 5](#interactive-tasks-introduced-in-evaluation-5)
    - [Agent Identification](#agent-identification)
    - [Moving Target Prediction](#moving-target-prediction)
    - [Navigation - Holes and Lava](#navigation---holes-and-lava)
    - [Navigation - Ramps](#navigation---ramps)
    - [Solidity](#solidity)
    - [Spatial Elimination](#spatial-elimination)
    - [Support Relations (Interactive Gravity Support)](#support-relations-interactive-gravity-support)
    - [Tools - Symmetric Tool Use](#tools---symmetric-tool-use)
  - [Introduced in Evaluation 6](#interactive-tasks-introduced-in-evaluation-6)
    - [Arithmetic and Number Comparison](#arithmetic-and-number-comparison)
    - [Imitation (Interactive)](#imitation-interactive)
    - [Occluded Trajectory and Collisions (Interactive)](#occluded-trajectory-and-collisions-interactive)
    - [Set Rotation](#set-rotation)
    - [Shell Game](#shell-game)
    - [Spatial Reference](#spatial-reference)
    - [Spatial Reorientation](#spatial-reorientation)
    - [Tools - Asymmetric Tool Use and Tool Choice](#tools---asymmetric-tool-use-and-tool-choice)
  - [Introduced in Evaluation 7](#interactive-tasks-introduced-in-evaluation-7)
    - [Hidden Set Rotation](#hidden-set-rotation)
    - [Knowledgeable Agents](#knowledgeable-agents)
    - [Tools - Secondary Tool Use](#tools---secondary-tool-use)
- [Passive Agent Tasks](#passive-agent-tasks)
  - [Overview](#passive-agent-overview)
  - [Data](#passive-agent-data)
    - [Evaluation Datasets](#passive-agent-evaluation-datasets)
    - [Training Datasets](#passive-agent-training-datasets)
  - [Introduced in Evaluation 3](#passive-agent-tasks-introduced-in-evaluation-3)
    - [Efficient Action](#efficient-action-passive-agent)
    - [Object Preference](#object-preference-passive-agent)
  - [Introduced in Evaluation 4](#passive-agent-tasks-introduced-in-evaluation-4)
    - [Inaccessible Goal](#inaccessible-goal-passive-agent)
    - [Instrumental Action](#instrumental-action-passive-agent)
    - [Multiple Agents](#multiple-agents-passive-agent)
  - [Introduced in Evaluation 6](#passive-agent-tasks-introduced-in-evaluation-6)
    - [Agent / Non-Agent](#agent--non-agent-passive-agent)
    - [Social and Instrumental Approach and Imitation](#social-and-instrumental-approach-and-imitation-passive-agent)
  - [Introduced in Evaluation 7](#passive-agent-tasks-introduced-in-evaluation-7)
    - [Helper / Hinderer](#helper--hinderer-passive-agent)
    - [True / False Belief](#true--false-belief-passive-agent)
- [Passive Physics Tasks](#passive-physics-tasks)
  - [Overview](#passive-physics-overview)
  - [Data](#passive-physics-data)
  - [Introduced in Evaluation 3](#passive-physics-tasks-introduced-in-evaluation-3)
    - [Object Permanence (Passive)](#object-permanence-passive-physics)
    - [Shape Constancy](#shape-constancy-passive-physics)
    - [Spatio-Temporal Continuity](#spatio-temporal-continuity-passive-physics)
  - [Introduced in Evaluation 3.5](#passive-physics-tasks-introduced-in-evaluation-35)
    - [Gravity Support (Passive)](#gravity-support-passive-physics)
  - [Introduced in Evaluation 4](#passive-physics-tasks-introduced-in-evaluation-4)
    - [Collisions (Passive)](#collisions-passive-physics)
- [Other Tasks](#other-tasks)
  - [Data](#other-data)
  - [Introduced in Evaluation 6](#other-tasks-introduced-in-evaluation-6)
    - [Seeing Leads to Knowing (Passive)](#seeing-leads-to-knowing-passive)
- [Evaluation](#evaluation)
- [Scoring](#scoring)
  - [Ambiguous and Control Trials](#ambiguous-and-control-trials)
  - [Scorecard](#scorecard)
- [Acknowledgements](#acknowledgements)
- [License](#license)

## Interactive Tasks

### Interactive Overview

Each trial, or "scene", for an interactive task occurs within a procedurally generated room in our 3D environment. Each interactive task requires that you use common-sense reasoning to find and pick up a goal object (soccer ball) located in the room. As requested, your system's efficiency does not prevent it from succeeding at these tasks (except for a very generous action/step limit), or impact its quantitative evaluation score, in order to allow for exploration-based approaches. Please note that the MCS python library returns a "reward" after each action/step that can be used for training, but is ignored during the evaluation. 

### Interactive Data

TODO DOWNLOAD

Training scenes for the following tasks can be made using the ILE Scene Generator: https://github.com/NextCenturyCorporation/mcs-scene-generator/

### Interactive Tasks Introduced in Evaluation 3

#### Retrieval - Containers

Summary:

Container Retrieval tasks require a common-sense understanding of containment. You must find the soccer ball, which may or may not be hidden inside a container (use OpenObject to open a closed container), and then use PickupObject on the ball to pick it up.

|||
|---|---|
![eval_7_interactive_containers_0001_02](https://github.com/NextCenturyCorporation/MCS/assets/10994382/c869ebb6-1017-4776-b8d6-e71ffcbaf434) | ![eval_7_interactive_containers_0001_05](https://github.com/NextCenturyCorporation/MCS/assets/10994382/df79d960-d24e-4cbc-9d86-82eff653b719)

Details:

- You start in a room containing many objects, including furniture and toys. Your goal is to find and pick up the soccer ball, located somewhere in the room.
- Sometimes the soccer ball will be located on the floor; other times it will be located inside a closed container.
- You can use the PickupObject action on the soccer ball to pick it up.
- You can use the OpenObject action on a closed container to open it.
- You can also try to use the OpenObject action on non-container objects, though it will fail.
- The evaluation data will have some "novel" containers which did not appear in your training data.

#### Retrieval - Obstacles

Summary:

Obstacle Retrieval tasks require a common-sense understanding of occlusion. You must find the soccer ball, which may or may not be hidden behind “obstacle” furniture (furniture which you can see through, but cannot walk through), and then use PickupObject on the ball to pick it up, which completes the scenario.

|||
|---|---|
![eval_7_interactive_obstacles_0001_06](https://github.com/NextCenturyCorporation/MCS/assets/10994382/ccd1a72d-075d-4667-a851-022a70379dc9) | ![eval_7_interactive_obstacles_0001_02](https://github.com/NextCenturyCorporation/MCS/assets/10994382/02a68b56-505b-4343-9a22-1de82f00cde6)

Details:

- You start in a room containing many objects, including furniture and toys. Your goal is to find and pick up the soccer ball, located somewhere in the room.
- The soccer ball will always be located on the floor, but sometimes it will be behind obstacle furniture: large pieces of furniture which you can see through/under but cannot navigate through (like tables and chairs).
- You can use the PickupObject action on the soccer ball to pick it up.
- The evaluation data will have some "novel" obstacle furniture which did not appear in your training data.

#### Retrieval - Occluders

Summary:

Occluder Retrieval tasks require a common-sense understanding of occlusion. You must find the soccer ball, which may or may not be hidden behind occluding furniture (furniture which you can neither see through nor walk through), and then use PickupObject on the ball to pick it up, which completes the scenario.

|||
|---|---|
![eval_7_interactive_occluders_0001_05](https://github.com/NextCenturyCorporation/MCS/assets/10994382/88a22883-ba64-439c-af1b-510222f41d8e) | ![eval_7_interactive_occluders_0001_06](https://github.com/NextCenturyCorporation/MCS/assets/10994382/337ec563-bf15-4b0e-a33f-dac10355e5d6)

Details:

- You start in a room containing many objects, including furniture and toys. Your goal is to find and pick up the soccer ball, located somewhere in the room.
- The soccer ball will always be located on the floor, but sometimes it will be hidden from your starting position's view behind occluding furniture: large pieces of furniture which you can neither see nor navigate through (like sofas and bookcases).
- You can use the PickupObject action on the soccer ball to pick it up.
- The evaluation data will have some "novel" occluding furniture which did not appear in your training data.

### Interactive Tasks Introduced in Evaluation 4

#### Object Permanence (Interactive)

Summary:

Interactive Object Permanence tasks require a common-sense understanding of object permanence. You must watch (using the Pass action) as a soccer ball is tossed through the air and lands hidden behind an occluder; you must then determine which side of the room contains the ball, find it, and use PickupObject on it, which completes the scenario. This is a “forced choice” task: once you walk off the platform onto one side of the room, you are unable to move to the other side of the room.

https://github.com/NextCenturyCorporation/MCS/assets/10994382/ce9a0b76-b565-46ef-8197-ce196395f356

https://github.com/NextCenturyCorporation/MCS/assets/10994382/774e9b0b-4dc5-4558-bb07-83be0d8eaad8

Details:

- You start on a tall platform bisecting the entire room (this is a "forced choice" task). Each side of the room contains an occluder (on the floor) and throwing device (on the wall). After the scene begins, one of the throwing devices will launch a soccer ball. The soccer ball will land behind one of the occluders, hidden from your view. You will have to understand which side of the room contains the soccer ball after it is hidden from view, jump off of the platform onto that side, navigate around the occluder, and pick up the soccer ball. As a "forced choice" task, once you leave the platform, you will not be able to navigate to the other side of the room (if you've chosen incorrectly).
- After the scene begins, you will be "frozen" (forced to only use Pass actions) until the soccer ball is launched and then lands behind an occluder.

### Interactive Tasks Introduced in Evaluation 5

#### Agent Identification

Summary:

Agent Identification tasks require a common-sense understanding of agency. You must identify the agent, approach it, use InteractWithAgent on the agent to request the soccer ball, and then use PickupObject on the ball once the agent produces it which completes the scenario. This is a “forced choice” task: once you walk off the platform onto one side of the room, you are unable to move to the other side of the room.

https://github.com/NextCenturyCorporation/MCS/assets/10994382/d9f7e054-8d46-467a-8d16-dcf126af8a81

https://github.com/NextCenturyCorporation/MCS/assets/10994382/0b27f91e-9d74-482c-8e2f-236930c28bb0

Details:

- You start on a tall platform bisecting the entire room. There will be an agent on one side of the room and a non-agent (a random object, like a sofa) on the other side of the room. As with our other interactive tasks, your goal is to “find and pickup the soccer ball”, but the soccer ball will not be visible. You will have to jump off the platform onto the side of the room containing the agent and request that the agent produce the soccer ball for you.
- The core goals of this task are learning:
   - How to identify an agent based on surface features (like faces) and self-propulsion (like breathing and walking).
   - To request help from an agent if the goal object (soccer ball) is not otherwise visible.
- In Eval 5, there will only be one agent in a scene, and the agent will always be able to produce the soccer ball upon request. However, these assumptions might change in future evals.
- Starting in release 0.5.3, there will be an InteractWithAgent action that facilitates the request for the agent to produce the soccer ball:
   - The agent will rotate across multiple action steps to face you, reach behind its back to retrieve the soccer ball, and offer the ball to you.
   - You can use the PickupObject action to pick up the ball from the agent’s hand.
   - You will have to use the Pass action multiple times to wait for the agent to finish performing its animation/movement before you can pick up the ball.
   - In future evals, the agent may instead refer you to the ball’s location via an animation like pointing.
- Starting in release 0.5.4, each agent can be configured to have a walking path.
- You will be able to walk across the full length of the platform before you jump off from it in order to verify that the soccer ball is not hiding behind any objects in the scene.

#### Moving Target Prediction

Summary:

Moving Target Prediction tasks require a common-sense understanding of trajectory. You are in a room with lava on both sides and a “safe zone” in the center. After spinning around to see the entire room (using the RotateRight action), you watch (using the Pass action) as a soccer ball is launched across the floor, toward the “safe zone”. You must move to intercept the ball and use PickupObject on it before it rolls into the lava and out of your reach. Walking into the lava immediately ends the scene (therefore failing the scenario).

https://github.com/NextCenturyCorporation/MCS/assets/10994382/22b4c78f-7eef-44a4-8e75-82306f12dc09

https://github.com/NextCenturyCorporation/MCS/assets/10994382/8b13cb6d-7fdd-48d9-94d4-9ba95ae6b073

https://github.com/NextCenturyCorporation/MCS/assets/10994382/aef99402-8029-476c-b431-6d931701fbe4

https://github.com/NextCenturyCorporation/MCS/assets/10994382/dd5b75e8-6612-4fb8-91e4-92a6e0217f43

Details:

- The core goal of this task is to understand the speed and trajectory of the soccer ball in order to intercept it. At the start of the scene, the ball will immediately be rolled out from the “thrower” on one of the side walls (grey tube) at a speed that should give your AI enough time to think and retrieve it before it rolls into a pool of lava (and out of reach) positioned across the other side of the room. As in the real world, the ball is affected by physical properties like drag and friction. The ball will remain in contact with the floor during its movement (no bouncing).
- At the start of the scene, before the soccer ball is rolled out from the thrower, your AI will be forced to rotate in a complete circle (using 36 sequential RotateRight actions), so it may see the initial landscape of the room.
- Like other interactive scenes, you use the PickupObject action to retrieve the ball.
- You will start on a platform so you can get a good view of the entire room, but can walk off the platform at any time as normal.
- See “Navigation: Lava” for more information on adjusting our lava settings for training.

#### Navigation - Holes and Lava

Summary:

Hole and Lava Navigation tasks require a common-sense understanding of navigation in a dangerous environment. You must walk through a room full of holes or lava in order to find the soccer ball, and then use PickupObject on the ball to pick it up, which completes the scenario. Walking into a hole will make it impossible to reach the ball (you fall in and cannot escape). Walking into the lava immediately ends the scene (therefore failing the scenario). Sometimes the ball is on the floor, and sometimes an agent is holding the ball instead (use InteractWithAgent on the agent to request the soccer ball).

https://github.com/NextCenturyCorporation/MCS/assets/10994382/a72a4686-f3b9-4667-972c-e1be53152c00

Details:

- Your AI will begin on a platform so it has a good view of the entire room before moving.
- If you move too close to a hole, you’ll fall in, and won’t be able to get out.
- Stepping too close to the lava will force you to immediately end the scene (you will only be allowed to use the “EndScene” action if you try to call the step function, or you can call end_scene yourself). This will be what happens during the evaluation. You can override the default setting using the steps_allowed_in_lava config property: https://nextcenturycorporation.github.io/MCS/install.html#steps-allowed-in-lava 
- Stepping too close to the lava will give you an insurmountably large reward penalty. You will always receive this penalty, even if you must immediately end the scene due to the steps_allowed_in_lava setting (see above). You can override the default setting using the lava_penalty config property: https://nextcenturycorporation.github.io/MCS/install.html#lava-penalty 
- Stepping too close to the lava will adjust the haptic_feedback and steps_in_lava properties of the StepMetadata output returned by that action step: haptic_feedback will be {"on_lava": true} and steps_in_lava will increase by one. https://nextcenturycorporation.github.io/MCS/api.html#machine_common_sense.StepMetadata
- Use the InteractWithAgent action to facilitates the request for the agent to produce the soccer ball. For more information about this action, please refer to the Details under the [Agent Identification](#agent-identification) task.

#### Navigation - Ramps

Summary:

Ramp Navigation tasks require a common-sense understanding of navigation in an environment with multiple stories. You must walk up and/or down one or more ramps in order to find the soccer ball, and then use PickupObject on the ball to pick it up, which completes the scenario. Sometimes the ball is on the floor, and sometimes an agent is holding the ball instead (use InteractWithAgent on the agent to request the soccer ball).

|||
|---|---|
![ramps_eval_5_ex_1](https://github.com/NextCenturyCorporation/MCS/assets/10994382/b2c87fde-ca3f-48cc-8ed4-597ceacc3d39) | ![ramps_eval_5_ex_3](https://github.com/NextCenturyCorporation/MCS/assets/10994382/33b9373a-77fd-4e9e-8050-88a9dd3a7a1c)

Details:

- Ramps will always be triangles/wedges. They can have angles up to 45 degrees. They will always be the same color/texture as their corresponding platform.
- Platforms can have either one or two levels. Each platform level will always have a different color/texture. Platforms will have “lips” (or edges) that surround their perimeter to make it impossible to move off the platform without using one of its corresponding ramps.

#### Solidity

Summary:

Solidity tasks require a common-sense understanding of objects and gravity. You must watch (using the Pass action) as a soccer ball is lowered by a pole, but the ball is hidden as it goes behind a large occluding wall before you see the pole release it; you must then determine which side of the room contains the ball, find it, and use PickupObject on it to pick it up, which completes the scenario. To access a part of the room, you must open one of the doors (using the OpenObject action) in the occluding wall: the left side of the room can be accessed using the left door; the right side of the room can be accessed using the right door; and the platform can be accessed using the middle door. This is a “forced choice” task: once you open the door to one part of the room, you are unable to access the other parts of the room.

https://github.com/NextCenturyCorporation/MCS/assets/10994382/392d5b5e-977f-4c75-a169-7a50f5752cf7

https://github.com/NextCenturyCorporation/MCS/assets/10994382/308d2d09-e4af-472b-93f4-9f626692bdde

Details:

- You start on a tall platform bisecting the entire room. Notably, there is an extension of the platform coming out of either its left or right side, which is only accessible by walking on top of the platform. Additionally, the far end of the platform has "lips" (or edges) that surround the platform and make it impossible to move off the platform to the ground on that end.
- Each solidity scene contains 3 phases. You will be frozen (only able to perform Pass actions) at the start (about 60 to 100 action steps), but later you will be able to act freely.
   - First, you will see a placer (pink cylinder) holding a soccer ball slowly descend from the ceiling and come to a stop either above the platform or in mid-air. Note that the placer hasn’t released its hold on the ball yet.
   - Second, you will see a large occluder descend from the ceiling between you and the soccer ball blocking most (but not all) of your view of the far end of the room. This occluder will have three doors: one on ground level to the left of the platform; one on ground level to the right of the platform; and one in the middle at platform level. Once this “door occluder” has finished descending, it will no longer move. (This door occluder moves and works the same as in the Interactive Support Relations task.)
   - Third, you will see the placer turn blue, indicating that it has released the soccer ball, and ascend back into the ceiling. However, due to the occluder, you can’t see the final position of the ball. You will then be unfrozen and must pickup the soccer ball to succeed in the trial. You will need to decide whether the ball has fallen to the ground on the left side (only accessible via the left door), the right side (only accessible via the right door), or the platform extension (only accessible via the middle door).
- A door can be opened using the OpenObject action. However, in these scenes, once you open one door, you will not be able to open another door.

#### Spatial Elimination

Summary:

Spatial Elimination tasks require a common-sense understanding of spatial elimination. This is a “forced choice” task: once you walk off the platform onto one side of the room, you are unable to move to the other side of the room. You must identify which side of the room has the soccer ball, find it, and then use PickupObject on the ball to pick it up, which completes the scenario.

|||
|---|---|
![spatial_elimination_eval_5_ex_1](https://github.com/NextCenturyCorporation/MCS/assets/10994382/9152594e-ca9f-43eb-a499-7b107d7fe406) | ![spatial_elimination_eval_5_ex_2](https://github.com/NextCenturyCorporation/MCS/assets/10994382/63df3f27-98df-46c0-888a-fc0887ae0708)
![spatial_elimination_eval_5_ex_3](https://github.com/NextCenturyCorporation/MCS/assets/10994382/83fa96da-fc7a-41c1-aa6a-42a4376443d8) | ![spatial_elimination_eval_5_ex_4](https://github.com/NextCenturyCorporation/MCS/assets/10994382/d3897fdc-3fdf-408a-97ee-a0f6784f23eb)

Details:

- Like the Interactive Object Permanence tasks from Eval 4, these scenes contain a tall platform bisecting the entire room. You’re forced to move off the platform to either side, but, once you’ve made a choice, you can’t access the other side.

#### Support Relations (Interactive Gravity Support)

Summary:

Interactive Gravity Support Relations tasks require a common-sense understanding of gravity. You must watch (using the Pass action) as a “container” holding a soccer ball is lowered by poles, but the container and the ball are hidden as they go behind a large occluding wall before you see the poles release them; you must then determine which side of the room contains the ball, find it, and use PickupObject on it to pick it up, which completes the scenario. The container is sometimes released fully onto the platform, fully onto the floor, or partially onto the platform, and possibly falling onto the floor. To access a part of the room, you must open one of the doors (using the OpenObject action) in the occluding wall: the left side of the room can be accessed using the left door; the right side of the room can be accessed using the right door; and the platform can be accessed using the middle door. This is a “forced choice” task: once you open the door to one part of the room, you are unable to access the other parts of the room.

https://github.com/NextCenturyCorporation/MCS/assets/10994382/436f1c93-8043-4599-adbc-e50dac0194ad

https://github.com/NextCenturyCorporation/MCS/assets/10994382/40caccb2-39d2-45ed-af55-8ed98657059b

Details:

- You start on a tall platform bisecting the entire room. Notably, the far end of the platform (beyond the door occluder) is raised to make it impossible to move forward on the platform past the middle door.
- Each support relations scene contains 3 phases. You will be frozen (only able to perform Pass actions) at the start (about 60 to 100 action steps), but later you will be able to act freely.
   - First, you will see two placers (pink cylinders) holding a container slowly descend from the ceiling and come to a stop above the platform, so that the width of the container is either fully above the platform or partially above the platform. The container will always be open-topped (i.e. you don’t have to “Open” it), either symmetric or asymmetric (from your view point), and holding the soccer ball (clearly visible). Note that the placers haven’t released their hold on the container yet.
   - Second, you will see a large occluder descend from the ceiling between you and the soccer ball blocking most (but not all) of your view of the far end of the room. This occluder will have three doors: one on ground level to the left of the platform; one on ground level to the right of the platform; and one in the middle at platform level. Once this “door occluder” has finished descending, it will no longer move. (This door occluder moves and works the same as in the Interactive Solidity task.)
   - Third, you will see the placers turn blue, indicating that they have released the container, and ascend back into the ceiling. However, due to the occluder, you can’t see the final position of the container or the ball. You will then be unfrozen and must pickup the soccer ball to succeed in the trial. You will need to decide whether the container and the ball were properly supported by the platform (only accessible via the middle door) or were not supported by the platform and have therefore fallen to the ground on either the left side (only accessible via the left door) or the right side (only accessible via the right door).
- A door can be opened using the OpenObject action. However, in these scenes, once you open one door, you will not be able to open another door.

#### Tools - Symmetric Tool Use

Summary:

Symmetric Tool Use tasks require a common-sense understanding of affordances. You must use a symmetric “tool” (a large rectangular object with wheels and a unique texture) to extract the soccer ball from the middle of a pool of lava (using PushObject or MoveObject to push the tool so it collides with the ball causing it to roll out from the lava), and then use PickupObject on the ball, which completes the scenario.

|||
|---|---|
![tool_use_eval_5_ex_1](https://github.com/NextCenturyCorporation/MCS/assets/10994382/e38e275b-99d3-4ce4-8851-28b6b1558d16) | ![tool_use_eval_5_ex_3](https://github.com/NextCenturyCorporation/MCS/assets/10994382/ebd8f106-e1d8-4db9-bb80-d3c79d386aca)

Details:

- Tools have their own object types that are all identical except in their length and width. They look like large grey rectangular prisms on wheels with a short cylinder sticking up from each corner. They have a unique grey hexagonal metallic texture. They are all low friction and light weight, to make them easy to push by force. https://nextcenturycorporation.github.io/MCS/schema.html#tool-objects
- The core goal of this task is for you to learn how to maneuver the tool object so it will collide with the soccer ball and cause it to roll from the lava into an accessible area of the room. To achieve this goal, we’ve prepared five actions for you to use with the tool object. All are acceptable to use during the evaluation.
   - PushObject and PullObject, which apply a force on the center of a specific object, either directly away from you (push) or directly toward you (pull), based on your current facing. A large applied force may persist across multiple action steps. Some force will be transferred onto lighter objects (like the soccer ball) that are contacted by the pushed/pulled object. Note that smaller and lighter objects will realistically move more than larger or heavier objects under equal amounts of force.
   - MoveObject, which moves a specific object forward, backward, left, or right by exactly 0.1 meter. This action does not apply any physical force. Lighter objects (like the soccer ball) that are contacted by the moved object will be moved out of the way in the appropriate direction.
   - TorqueObject, which applies a rotational force on the center of a specific object, either clockwise or counter-clockwise. A large applied force may persist across multiple action steps. Note that smaller and lighter objects will realistically rotate more than larger or heavier objects under equal amounts of force.
   - RotateObject, which rotates a specific object clockwise or counter-clockwise by exactly 5 degrees. This action does not apply any physical force.
   - See the full action documentation here: https://nextcenturycorporation.github.io/MCS/api.html#machine_common_sense.Action 
- See the section on the new lava task for more information about using lava.
- Please note: while only Pushing tools (or Moving them forward) will be necessary in Eval 5, future evals might require Pulling tools (or Moving them backward).

### Interactive Tasks Introduced in Evaluation 6

#### Arithmetic and Number Comparison

Summary:

Number Comparison tasks require a common-sense understanding of numbers. This is a “forced choice” task: once you walk off the platform onto one side of the room, you are unable to move to the other side of the room. You must identify which side of the room has the most soccer balls and use PickupObject on each of them to pick them up which completes the scenario. Sometimes the balls become occluded so you have to remember how many were originally present on each side.

Arithmetic tasks require a common-sense understanding of addition and subtraction. This is a “forced choice” task: once you walk off the platform onto one side of the room, you are unable to move to the other side of the room. You must watch (using the Pass action) as zero or more soccer balls are added to or subtracted from each side of the room. Then you must identify which side of the room has the most reachable soccer balls and use PickupObject on each of them to pick them up which completes the scenario. Sometimes the addition/subtraction is occluded so you have to remember how many balls were added to or subtracted from each side.

https://github.com/NextCenturyCorporation/MCS/assets/10994382/57b6acc4-1cde-4e82-b56f-2aa23b8bced2

https://github.com/NextCenturyCorporation/MCS/assets/10994382/de4b01ea-5f48-46ac-83df-edd77776bcc0

https://github.com/NextCenturyCorporation/MCS/assets/10994382/87d6fe2a-97c6-4308-9340-70258245ae85

https://github.com/NextCenturyCorporation/MCS/assets/10994382/e2f4028f-7f2a-4004-9e22-967bc12c012f

https://github.com/NextCenturyCorporation/MCS/assets/10994382/fbe1d7a8-dfff-4001-97e0-4d7f8c40b372

Details:

- You start on a platform bisecting the room (this is a forced choice task). One or more objects (soccer balls) are positioned on each side of the room. Like our other forced choice tasks, once you “hop off” the platform onto one side of the room, you cannot reach the other side. You must determine which side of the room contains more potential “target” objects, and pick up all of the objects on that side of the room.
- In Number Comparison tasks, you can move immediately. Nothing will change in the scene while it is running.
- In Arithmetic tasks, objects will either be added or subtracted from one side of the room. Immediately after the scene is loaded, one or more placers descend from the ceiling. The placers either hold new objects (soccer balls) and drop them on the floor, or pick up existing objects and raise them to the ceiling, making them unavailable. This may mean that the side of the room which had the most potential “target” objects when the scene was first loaded now no longer has the most.
   - In Evaluation 6, scenes will not have both addition and subtraction – just one mathematical operation.
   - In Evaluation 6, objects will only be added/subtracted on one side of the room.
   - Sometimes all placers will remain empty, to represent addition/subtraction by zero.
- Some Arithmetic scenes will contain occluders, which are lowered into the room on both sides after the scene is loaded. You will be able to see the initial number of objects on each side, and you will be able to see how many objects are added to, or subtracted from, the scene, but you will not be able to see the final number of objects at rest before you are forced to “hop off” the platform (choose a side of the room).
- In both tasks, each side of the room may have between zero and five potential “target” objects.

Notes:

- These scenes use the new “multi retrieval” interactive goal category, to distinguish them from scenes with the existing “retrieval” category, which have only a single target. For more information on “multi retrieval” interactive goals, please see our API doc here: https://nextcenturycorporation.github.io/MCS/api.html#machine_common_sense.GoalCategory.MULTI_RETRIEVAL
- You will not receive a reward until all of the targets are picked up.
- In Arithmetic scenes, you will be restricted to only using Pass actions until the placers (and occluders) are finished moving.

#### Imitation (Interactive)

Summary:

Interactive Imitation tasks require a common-sense understanding of agency. You must watch (using the Pass action) as an agent perform a series of actions (opening one or more chests in a specific order) in order to access a soccer ball; then the room is “reset” (using the EndHabituation action) and you must perform the same actions in the same order (using the OpenObject action on the correct chests). Then you will be able to reach the soccer ball, and you can use PickupObject on it to pick it up, which completes the scenario. Performing the wrong actions (opening the wrong chests, or opening them in the wrong order) automatically fails the scenario. Sometimes you or the chests are repositioned when the room is reset.

https://github.com/NextCenturyCorporation/MCS/assets/10994382/1536702f-b2b6-4323-9da6-fc7af4bff486

https://github.com/NextCenturyCorporation/MCS/assets/10994382/cde91660-af4d-4289-91e5-689c38a59290

https://github.com/NextCenturyCorporation/MCS/assets/10994382/7a297753-d3c8-499a-8982-d3f2237ba146

https://github.com/NextCenturyCorporation/MCS/assets/10994382/526e2211-be7d-40cc-b62c-23ae09bd2bbe

Details:

- You start in a room looking at three containers lined up in a row. The containers are identical in size and shape (chest_1) but have different colors. After the scene begins, an agent approaches either one or two specific container(s) and opens them in a specific order, triggering a placer holding the target object (soccer ball) to descend from the ceiling, release the target object onto the floor, and ascend back into the ceiling. You are then kidnapped, during which the room is reset: the placer picks up the target object and raises it back up toward the ceiling, making the target object inaccessible; the containers are closed; and the agent moves out-of-the-way. You must remember the pattern the agent used to make the target object accessible, open the correct containers in the correct order, and pick up the target object when it is within your reach.
- The room always has three containers. Sometimes you need to open two containers; other times you only need to open one container.
- Sometimes you will be moved to a new location when you are kidnapped; other times you will remain in the same location.
- Sometimes the containers will be moved to a new location when you are kidnapped; sometimes they will be rotated; other times they will remain in the same location. If the containers are moved or rotated, they will always remain adjacent to each other, and in the same order relative to each other.

Notes:

- Imitation scenes use the new “imitation” interactive goal category to differentiate them from normal “retrieval” goals. For more information on “imitation” goals, please see our API doc here: https://nextcenturycorporation.github.io/MCS/api.html#machine_common_sense.GoalCategory.IMITATION
- You will be restricted to only using Pass actions until being kidnapped. While “frozen”, you will be able to see all of the containers, the agent, and the target object, once it has been released by the placer.
- The containers always start lined up on either the left side of your view, or the right side. The agent will approach the containers from the opposite side.
- Kidnapping and teleporting are performed using the EndHabituation action. Like other uses of this action, you will receive a blank frame during the kidnapping step. Unlike how this action worked in Eval 4, you will not receive any information (position/rotation) about the teleport destination (this information is now tracked internally by the MCS environment).
- Containers are opened using the OpenObject action, like in other scenes with containers.
- If you open an incorrect container, or you open the correct containers in an incorrect order, you will immediately be forced to end the scene without continuing further, thus failing the trial.

#### Occluded Trajectory and Collisions (Interactive)

Summary:

Occluded Trajectory tasks require a common-sense understanding of trajectory. You must watch (using the Pass action) as a soccer ball is launched across the floor, but you do not see its entire trajectory, due to a large occluding wall which descends in front of you; you must then determine which side of the room contains the soccer ball, find it, and use PickupObject on it to pick it up, which completes the scenario. To access a side of the room, you must open one of the doors (using the OpenObject action) in the occluding wall. This is a “forced choice” task: once you open the door to one side of the room, you are unable to access the other side of the room (because it is blocked by lava).

Interactive Collision tasks require a common-sense understanding of trajectory and collision. You must watch (using the Pass action) as a green “shooter ball” is launched across the floor toward a stationary soccer ball, but you do not see the entire trajectory (and, sometimes, even the collision itself), due to a large occluding wall which descends in front of you; you must then determine which side of the room contains the soccer ball, find it, and use PickupObject on it to pick it up, which completes the scenario. To access a side of the room, you must open one of the doors (using the OpenObject action) in the occluding wall. This is a “forced choice” task: once you open the door to one side of the room, you are unable to access the other side of the room (because it is blocked by lava).

https://github.com/NextCenturyCorporation/MCS/assets/10994382/898d48b4-0c26-4a4c-9cf2-4de22e765059

https://github.com/NextCenturyCorporation/MCS/assets/10994382/4b2a5a02-24b3-49ef-a700-43abc37d56de

https://github.com/NextCenturyCorporation/MCS/assets/10994382/8b8bf840-52d0-4f13-a490-5f2c5b7f374f

https://github.com/NextCenturyCorporation/MCS/assets/10994382/97f421d2-eb72-4e1a-8437-b68d2e551d1e

Details:

- Interactive Trajectory – You start on a platform, and a strip of lava is bisecting the room (this is a forced choice task). A throwing device (or "thrower") is positioned across the room from you (within your initial view) holding the target object (soccer ball). Immediately after the scene begins, the thrower "launches" the target object so it starts to roll across the room. An occluding wall with two doors (or "two-door-occluder") descends from the ceiling while the target object is rolling, obstructing your view of the target object's complete trajectory and final position. You must determine whether the target object will end on either the left side or the right side of the room/lava, using your knowledge of its trajectory; then you must jump off from the platform on the correct side, walk up to the corresponding door, open it, find the target object, and pick it up.
- Interactive Collision – You start on a platform, and a strip of lava is bisecting the room (this is a forced choice task). A throwing device (or "thrower") is positioned across the room from you (within your initial view) holding a green ball, which is NOT the target object. The target object (soccer ball) is positioned elsewhere in the room (within your initial view), but not in the lava. Immediately after the scene begins, the thrower "launches" the green ball so it starts to roll across the room. The green ball either collides directly with the target object, hitting it "head-on", or completely misses the target object. An occluding wall with two doors (or "two-door-occluder") descends from the ceiling either immediately before or immediately after the collision, obstructing your view of the target's complete trajectory and final position. You must determine whether the target object will end on either the left side or the right side of the room/lava, using your knowledge of the green ball's trajectory and the possibility of a collision; then you must jump off from the platform on the correct side, walk up to the corresponding door, open it, find the target object, and pick it up.
- Sometimes the thrower will be oriented straight ahead, and the target object will remain on the same side of the room as it started; sometimes the thrower will be angled, and the target object will roll over the lava to the other side of the room.
- Sometimes the two-door-occluder will begin to descend immediately after the scene begins; sometimes it will wait a few steps, letting you see more of the target object's trajectory (or, in the Interactive Collisions task, the green ball's trajectory).
- Rolling over the lava does not affect the target object's movement any differently than rolling over the floor. Its movement is otherwise executed using our real-world physics simulation engine and is therefore affected by consistent physical properties like drag and friction.
- You can safely assume that the target object will never be launched with such a force or angle to cause it to "rebound" off a wall and cross over the lava to the other side of the room.
- If you step into the lava, you will be forced to immediately end the scene, thus failing it. Therefore, once you "jump off" the starting platform onto one side of the room, you will not have any way to cross over to the other side of the room.
- In the Interactive Collisions task, the green ball in the thrower will always appear the same. Nothing else in the room will be green.

Notes:

- You will be restricted to only using Pass actions until the door-occluder has finished descending. For more information on action restrictions, see the action_list property in the StepMetadata class: https://nextcenturycorporation.github.io/MCS/api.html#machine_common_sense.StepMetadata
- Stepping too close to the lava will force you to immediately end the scene (you will only be allowed to use the “EndScene” action if you try to call the step function, or you can call end_scene yourself). This will be what happens during the evaluation. You can override the default setting using the steps_allowed_in_lava config property: https://nextcenturycorporation.github.io/MCS/install.html#steps-allowed-in-lava
- Stepping too close to the lava will give you an insurmountably large reward penalty. You will always receive this penalty, even if you must immediately end the scene due to the steps_allowed_in_lava setting (see above). You can override the default setting using the lava_penalty config property: https://nextcenturycorporation.github.io/MCS/install.html#lava-penalty
- Stepping too close to the lava will adjust the haptic_feedback and steps_in_lava properties of the StepMetadata output returned by that action step: haptic_feedback will be {"on_lava": true} and steps_in_lava will increase by one. https://nextcenturycorporation.github.io/MCS/api.html#machine_common_sense.StepMetadata

#### Set Rotation

Summary:

Set Rotation tasks require a common-sense understanding of tracking objects as they move. You must watch (using the Pass action) as a soccer ball is deposited into one of the containers in the room, and lids are placed on all of the containers. Then either you will continue watching as the “turntable” (the large grey cog) rotates, or you will be forced to partially (or fully) circumnavigate the turntable using a series of Move and Rotate actions. You must identify which container holds the soccer ball, approach it, use OpenObject on it to open it, and then use PickupObject on the ball to pick it up, which completes the scenario. This is a “forced choice” task: once you open one container, you are unable to open other containers.

https://github.com/NextCenturyCorporation/MCS/assets/10994382/b44fcc48-b7de-433a-b520-bf36371206ac

https://github.com/NextCenturyCorporation/MCS/assets/10994382/c293ea74-1f77-4985-8f23-8d73ec88e00d

Details:

- You start in a room looking at a turntable (cog). Between one and five identical open containers are positioned on top of the turntable so they can be seen clearly. After the scene begins, a placer holding the target object (soccer ball) descends from the ceiling and releases the target object into one of the containers. Then placers holding lids descend from the ceiling and release the lids, attaching one to the top of each container. Finally, the turntable rotates either 90, 180, 270, or 360 degrees, either clockwise or counter-clockwise, moving the containers along with it. You must determine which container holds the target object, walk up to that container, open it, and pick up the target object.
- When you open a container, the other containers will automatically become locked (this is a forced choice task). So if the first container you open is not the correct container, you will never be able to retrieve the target object, and will therefore fail the trial.
- In some scenes, instead of the turntable rotating, you will be forced to move around the turntable, to either the left or the right, so you end facing the turntable and containers from a different angle. Please see the Engineering Details below for more information.
- The turntable will only ever rotate the one time at the beginning. In scenes with forced movement, the turntable will never rotate.

Notes:

- You will be restricted to only using Pass actions until the turntable finishes rotating (or, in some scenes, until you are forced to move). While “frozen”, you will be able to clearly see all of the containers, the turntable, and the target object as it is placed into a container.
- In some scenes, forced movement will be performed by returning the action you must invoke in your next controller.step call (like "MoveLeft" or "MoveRight") via the StepMetadata.action_list property, in the same way you are forced to use only “Pass” actions during other specific steps (see the previous bullet).
- In Eval 6, the containers and lids in these scenes are always the same size, shape, and color.
   - These containers can be opened using the OpenObject action, just like other containers. The lid will always open on the opposite side from where you are standing.
   - These containers will be a consistent shape (cuboid) and color (green) for all Eval 6 scenes, which we hope will simplify the training of your systems. New shapes or colors may be introduced in Eval 7.
   - Scenes with these containers will restrict you to use only Pass actions before the lid is placed onto the container, which happens at the beginning of the trial, before the “exploration” phase.
   - Your teams are able to use the ILE Scene Generator to make scenes with these containers (either with the lid on them from the start of the scene, or with the lid placed on them by a placer during the course of the scene) – please see our ILE API documentation for details.
- Information about the turntables (giant grey rotating cogs):
   - Turntables in evaluation scenes will rotate at a consistent speed of 5 degrees per action step, either clockwise or counter-clockwise.
   - Objects and agents on top of a turntable (including the AI) will rotate along with the turntable.
   - Turntables will be a consistent height, shape (cog), and color (grey) for all Eval 6 scenes, though their radii may change across different scenes.
   - Scenes with turntables will restrict you to use only Pass actions while the turntable is rotating, which happens at the beginning of the trial, before the “exploration” phase.

#### Shell Game

Summary:

Shell Game tasks require a common-sense understanding of tracking objects as they move. You must watch (using the Pass action) as a soccer ball is deposited into one of the containers in the room, and lids are placed on all of the containers; then poles will descend from the ceiling and move one or more of the containers to new locations. You must identify which container holds the soccer ball, approach it, use OpenObject on it to open it, and then use PickupObject on the ball to pick it up, which completes the scenario. This is a “forced choice” task: once you open one container, you are unable to open other containers. Please note that sometimes the containers are moved before the soccer ball is deposited.

https://github.com/NextCenturyCorporation/MCS/assets/10994382/e0127554-36a6-4526-892c-bcc1341c2b7e

https://github.com/NextCenturyCorporation/MCS/assets/10994382/6a5ed2f0-b8b2-410f-a744-38cdab9b9a27

https://github.com/NextCenturyCorporation/MCS/assets/10994382/98730a4a-a201-4cdf-8162-218188c26ec2

https://github.com/NextCenturyCorporation/MCS/assets/10994382/107232ca-f28a-4cc0-85ff-22d189b61daa

Details:

- You start in a room looking at two or three identical open containers positioned in a line near each other. After the scene begins, a placer holding the target object (soccer ball) descends from the ceiling and releases the target object into one of the containers. Then placers holding lids descend from the ceiling and release the lids, attaching one to the top of each container. Finally, a placer descends from the ceiling, attaches itself to the container holding the target object, drags the container across the floor to a new location, and releases the container. This dragging motion always moves the container toward you, then sideways, then away from you, which sometimes occludes your view of the other container(s).  You must determine which container holds the target object, walk up to that container, open it, and pick up the target object.
- When you open a container, the other containers will automatically become locked (this is a forced choice task). So if the first container you open is not the correct container, you will never be able to retrieve the target object, and will therefore fail the trial.
- In some scenes, the container will be dragged before the target object is placed into it and the containers' lids are attached.
- In some scenes, another placer will descend from the ceiling, attach itself to a second container (one that is not holding the target object), drag it across the floor to a new location, and release it. This means that two of the containers will have moved since the beginning of the scene.

Notes:

- You will be restricted to only using Pass actions until the lids are attached to their respective containers. While “frozen”, you will be able to clearly see all of the containers and the target object as it is placed into a container.
- In Eval 6, the containers and lids in these scenes are always the same size, shape, and color.
   - These containers can be opened using the OpenObject action, just like other containers. The lid will always open on the opposite side from where you are standing.
   - These containers will be a consistent shape (cuboid) and color (green) for all Eval 6 scenes, which we hope will simplify the training of your systems. New shapes or colors may be introduced in Eval 7.
   - Scenes with these containers will restrict you to use only Pass actions before the lid is placed onto the container, which happens at the beginning of the trial, before the “exploration” phase.
   - Your teams are able to use the ILE Scene Generator to make scenes with these containers (either with the lid on them from the start of the scene, or with the lid placed on them by a placer during the course of the scene) – please see our ILE API documentation for details.

#### Spatial Reference

Summary:

Spatial Reference tasks require a common-sense understanding of agency. You must watch (using the Pass action) as both an agent and a “blob” move and “point” to a container on one side of the room. You must use the agent’s point (and ignore the blob) to determine which container holds the soccer ball, approach it, use OpenObject to open it, and then use PickupObject on the ball to pick it up, which completes the scenario. This is a “forced choice” task: once you walk off the platform onto one side of the room, you are unable to move to the other side of the room. Agents can be identified by their facial features (blobs don’t have faces) and their autonomous movement (blobs “move” by rotating on turntables).

https://github.com/NextCenturyCorporation/MCS/assets/10994382/862044cd-7c33-4174-8677-f3aaacf691a6

https://github.com/NextCenturyCorporation/MCS/assets/10994382/31d8d9a4-7f22-4a21-bc0a-b5788ad88f2f

https://github.com/NextCenturyCorporation/MCS/assets/10994382/6400a0a9-e26e-4c64-9878-5f26394082f6

https://github.com/NextCenturyCorporation/MCS/assets/10994382/db675a03-0de2-4167-a9d7-a119d1e5a43a

https://github.com/NextCenturyCorporation/MCS/assets/10994382/e6d066e5-94ed-4287-bdfb-9ca796ded65d

Details:

- You start on a platform bisecting the room (this is a forced choice task). Each side of the room contains an identical closed container. One side of the room contains an agent who, after the scene begins, turns, walks toward, looks at, and points at the container secretly holding the target object (soccer ball). The agent keeps pointing at the container indefinitely. The other side of the room contains an unknown, faceless, blob-shaped entity (known as a “blob”) with a nose-like protrusion. The blob is positioned on a turntable (cog), and the turntable rotates so the blob’s “nose” is “pointing” at one of the containers, which may or may not be the same container at which the agent is pointing. Like our other forced choice tasks, once you “hop off” the platform onto one side of the room, you cannot reach the other side. You must determine which entity is the real agent, use the agent’s referential information (the direction of its walk, gaze, and point) to correctly identify the container holding the target object, walk up to that container, open it, and pick up the target object.
- The agent’s walk, gaze, and point will always be oriented in the same direction. This redundancy was introduced to make it easier for you to interpret the agent’s referential information.
- The container holding the target object will sometimes be on the side of the room with the agent, and other times be on the side of the room across from the agent.
- In some scenes, the agent will move and point before the turntable below the blob begins to rotate; in other scenes, the turntable will rotate fully before the agent begins to move.
- Some scenes will not have a blob – just an agent.
- For consistency, there is always a second turntable positioned underneath the agent, but it never rotates. Agents move on their own accord, but blobs cannot move by themselves. (This is another indication of agency.)

Notes:

- You will be restricted to only using Pass actions until the agent and turntable have stopped moving/rotating. While “frozen”, you will be able to clearly see the two containers, the agent, the blob, and the two turntables.
- Since the blobs are unknown entities by design, training scenes containing blobs will not be available. We have provided an example YAML configuration file for the ILE Scene Generator which uses everyday objects (like toy cars or wooden animals) in place of blobs.

#### Spatial Reorientation

Summary:

Spatial Reorientation tasks require a common-sense understanding of spatial landmarks. After spinning around to see the entire room (using the RotateRight action), you must watch (using the Pass action) as a soccer ball is deposited into a container on one side of the room; then you are “kidnapped” (using the EndHabituation action) and either kept on the same side of the room or moved to the opposite side. You must use landmarks (sometimes the room has a trapezoidal shape, a differently-colored wall, or a piece of furniture) to identify which side of the room has the soccer ball, find it, and then use PickupObject on the ball to pick it up, which completes the scenario. This is a “forced choice” task: once you walk off the platform onto one side of the room, you are unable to move to the other side of the room.

https://github.com/NextCenturyCorporation/MCS/assets/10994382/97fb77f4-9f35-41ee-9a7b-2efb649b8362

https://github.com/NextCenturyCorporation/MCS/assets/10994382/cf3e2b27-a4e0-4e1d-a165-425d9f1fc84b

https://github.com/NextCenturyCorporation/MCS/assets/10994382/27cfab0a-2b83-4fb5-b9af-665c1f05ed89

https://github.com/NextCenturyCorporation/MCS/assets/10994382/a49184c7-211d-4c8d-870e-b0d286f7a4db

Details:

- You start on a platform bisecting the room (this is a forced choice task). Two identical open-topped containers are positioned in mirrored locations on each side of the room (the left and right). A placer holding the target (soccer ball) descends from the ceiling over one of the containers and drops it into the container. You are then “kidnapped” and teleported to either the front or the back of the room, but still standing on the platform. Like our other forced choice tasks, once you “hop off” the platform onto one side of the room, you cannot reach the other side. You must determine which side of the room contains the target, move over to it and pick it up.
- Most scenes provide cues so you can determine whether you have been teleported to the opposite side of the room:
   - Sometimes either the left or right wall is a significantly different color than the other walls.
   - Sometimes the room is shaped like a trapezoid: the left and right walls are angled inward, and either the front or back wall is shorter.
   - Sometimes there is a large non-structural object, like a piece of furniture, on one side of the room; this is called an “unstable landmark.” In scenes containing both a stable landmark (differently colored room walls, or trapezoidal shaped rooms) and an unstable landmark (large objects like furniture that could theoretically be moved by an adult), your system should trust the location of the stable landmark more than the unstable landmark.
   - It should be impossible to see inside the containers from your position on top of the platform due to the position of the containers and a barrier on the platform that stops you from moving too far forward.

Notes:

- Immediately after the scene is loaded, but before the placers start moving, you will be forced to rotate in a full circle (using the RotateRight action 36 times in a row), so you can see the complete layout of the room before you are kidnapped. Then, you will be restricted to only using Pass actions until the placers are finished moving, and after you have been kidnapped.
- Kidnapping and teleporting are performed using the EndHabituation action. Like other uses of this action, you will receive a blank frame during the kidnapping step. Unlike how this action worked in Eval 4, you will not receive any information (position/rotation) about the teleport destination (this information is now tracked internally by the MCS environment).
- Whenever you are kidnapped, you we be teleported a little “off-center”, regardless of whether you remain on the same side of the room (near the “back” wall) or the opposite side (near the “front” wall). For example, if your original position is (X=0, Z=-7.5), your new position may be (X=0.1, Z=-7.6)

#### Tools - Asymmetric Tool Use and Tool Choice

Summary:

Asymmetric Tool Use tasks require a common-sense understanding of affordances. You must use an asymmetric “tool” (a large L-shaped object with wheels and a unique texture) to extract the soccer ball from the middle of a pool of lava (using PullObject or MoveObject to pull the tool so it collides with the ball causing it to roll out from the lava), and then use PickupObject on the ball, which completes the scenario. Sometimes the tool must be rotated (using RotateObject or TorqueObject) before it is pulled.

Tool Choice tasks require a common-sense understanding of affordances. Like the Symmetric Tool Use task, you must use a symmetric “tool” (a large rectangular object with wheels and a unique texture) to extract the soccer ball from the middle of a pool of lava (using PushObject or MoveObject to push the tool so it collides with the ball causing it to roll out from the lava), and then use PickupObject on the ball and complete the scenario. Sometimes the tool must be rotated (using RotateObject or TorqueObject) before it is pushed. This is a “forced choice” task: once you walk off the platform onto one side of the room, you are unable to move to the other side of the room. One side of the room contains a tool that can be used successfully to retrieve the soccer ball, while the other side contains a tool that is broken, inaccessible, or not a useful size.

|||
|---|---|
![tool_choice_ex_1](https://github.com/NextCenturyCorporation/MCS/assets/10994382/20668ccc-bffd-4b3d-9fdc-f775766687b3) | ![tool_hooked_ex_1](https://github.com/NextCenturyCorporation/MCS/assets/10994382/01587ca1-3e64-4a9b-8a03-5415fd26fb5b)

Details:

- Asymmetric Tool
   - The Asymmetric Tool task is a new variant of the Tool Use task from Eval 5. Rather than pushing a symmetric tool (a.k.a. “rectangular-shaped tool”), you must pull an asymmetric tool (a.k.a. “hooked tool” or “L-shaped tool”) to extract the target object (soccer ball) from the middle of a pool of lava (by pulling the tool so it comes into contact with the soccer ball and causes the ball to roll out from the lava to a safe, reachable area).
   - The pool of lava in Asymmetric Tool scenes always extends out to three of the exterior walls of the room, so you will not be able to extract the target object by only pushing the tool – you must also learn how to pull the tool, and how to identify situations in which doing so is necessary.
- Tool Choice
   - The Tool Choice task is similar to the Tool Use task from Eval 5, but in a forced choice paradigm. You start on a platform bisecting the room. Each side of the room contains a pool of lava surrounding a soccer ball. One side of the room has a tool that can be used to extract the soccer ball from the pool of lava in order to pick it up (by pushing the tool so it comes into contact with the soccer ball and causes the ball to roll out from the lava to a safe, reachable area). The soccer ball on the other side of the room is inaccessible. Like our other forced choice tasks, once you “hop off” the platform onto one side of the room, you cannot reach the other side. You must determine which side of the room contains the “useful tool”, correctly use the tool to extract the soccer ball from the pool of lava, and pick up the soccer ball.
   - The other side of the room may contain: no tool; a tool that is too small and thus cannot be used to successfully extract the soccer ball from the pool of lava; a tool that is broken into multiple pieces which are too small; or a tool that is completely separated from the soccer ball by an obstruction and thus cannot reach the soccer ball.

Notes:
- Asymmetric Tool
   - To pull an object, you may use either the PullObject action, which applies a force to the object using the environment’s physics engine, or the MoveObject action, which moves the object by an exact amount (0.1 meter) in a specified direction, bypassing the physics engine completely. Both actions will be valid during the evaluation.
   - Like the original Tool Use task, the asymmetric tool may need to be rotated (using the RotateObject and/or TorqueObject actions) before it can be used effectively.
- Tool Choice
   - For scoring purposes, only the soccer ball on the side of the room containing the “useful tool” is considered the “target object”.
   - In Eval 6, the “useful tool” in Tool Choice scenes will always be a symmetric (rectangular-shaped) tool (not an asymmetric tool).

### Interactive Tasks Introduced in Evaluation 7

#### Hidden Set Rotation

Summary:

TODO

https://github.com/NextCenturyCorporation/MCS/assets/10994382/0b22f8c2-6774-4cc0-a4e6-9fc0b0b3201b

https://github.com/NextCenturyCorporation/MCS/assets/10994382/1868299b-f26a-4692-8cfd-63dafe25557a

Details:

- This task is setup exactly like the Eval 6 Set Rotation task, but a giant “tube occluder” descends from the ceiling to hide the turntable’s rotation. Your goal is still to find and pick up the target object.
- For scenes in which the turntable would rotate, the tube occluder goes down just before the turntable begins to rotate (after the lids are placed onto the containers). The tube occluder goes up again after enough time for the turntable to rotate 360 degrees (even if the turntable rotates less than that).
- For scenes in which you are forced to move around the turntable, the tube occluder goes down just before the forced movement (after the lids are placed onto the containers). The tube occluder goes up again after enough time for your agent to circumnavigate the turntable a full 360 degrees (even if your agent moves less than that).
- You can assume the only change hidden by the tube occluder is the turntable rotating between 0 and 360 degrees.
- When you open a container, the other containers will automatically become locked. So if the first container you open is not the correct container, you will never be able to retrieve the target object, and will therefore fail the trial.

#### Knowledgeable Agents

Summary:

TODO

https://github.com/NextCenturyCorporation/MCS/assets/10994382/6fe0e811-b53b-4171-95dc-c0496440379b

https://github.com/NextCenturyCorporation/MCS/assets/10994382/0afc8420-f068-4767-904e-b3afc87621d9

Details:

- You begin positioned in the center of the back of the room, looking forward. A platform bisects the room (this is a forced choice task), and the target object (soccer ball) starts visible on top of the platform. An open container is positioned on each side of the platform, as well as a simulation-controlled agent. Each agent is facing either toward you (and can therefore see both containers) or away from you (and cannot see either container).
- Immediately after the scene begins, the two simulation-controlled agents rotate 180 degrees, reversing their orientations, and remain in these orientations until they turn to point (after the occluder rises up to the ceiling – see below). This rotation should help you identify which way the agent is facing (i.e. the front of their head versus the back).
- After this rotation, an occluder descends from the ceiling to hide your view of the containers and the target object. The simulation-controlled agents are on the same side of the occluder as the containers and target object. Importantly, the occluder is short enough so you can always see the faces of the two agents, and therefore you always know whether each agent can see the containers (because it's facing toward you) or cannot see the containers (because it’s facing away from you).
- Then, two “placers” (blue and pink poles) descend from the ceiling, one after another, and appear to pick up the target object, carry it across to one of the containers, and release the target object into that container. One of these placers is a decoy, but you cannot see which placer actually picked up the target object, or which container it was dropped into, due to the occluder. However, any simulation-controlled agents facing toward you can see the placers, containers, and target object.
- Next, two more placers descend from the ceiling and attach lids to the containers, and the occluder rises up to the ceiling, so you can see the two closed containers.
- Finally, each simulation-controlled agent turns and points to the container they believe holds the target object. Your goal, like in all interactive tasks, is to pick up the target object. To achieve your goal, you must determine which agent is knowledgeable (based on your understanding of whether that agent could see where the target object was placed), determine which container the knowledgeable agent is pointing at, move to that container, open it, and pick up the target object. Like our other forced choice tasks, once you “hop off” the platform onto one side of the room, you cannot reach the other side.
- Sometimes the knowledgeable agent will be on the platform furthest away from you, and sometimes the knowledgeable agent will be in the pit and therefore closer to you.

Notes:

- You will be “frozen” (restricted to only using Pass actions) and thus unable to move until after the simulation-controlled agents point.
- Using the InteractWithAgent action on an agent while it's pointing will not provide you with any additional information.

#### Tools - Secondary Tool Use

Summary:

TODO

https://github.com/NextCenturyCorporation/MCS/assets/10994382/a0a00f40-e9f7-4cbd-9521-c8c7e47e129d

https://github.com/NextCenturyCorporation/MCS/assets/10994382/292e188a-0429-42a8-b499-1df11013b14f

Details:

- You begin positioned randomly in a room containing two sections of lava. The first section of lava surrounds the target object (soccer ball). The second section of lava surrounds a hooked (L-shaped) tool. There is also a rectangular tool somewhere in the room. Neither the target object nor the hooked tool are within your reach due to the lava. Your goal, like in all interactive tasks, is to pick up the target object. To achieve your goal, you must know how to use the rectangular tool to push the hooked tool out from the lava, then use the hooked tool to pull the target object out from the lava.
- The position of the target object in the room, and the amount of lava surrounding it, will make it impossible for you to use the rectangular tool alone to push the target object out from the lava (and bypass using the hooked tool).
- The rectangular tool may start in proper alignment with the hooked tool, or may require you to move and/or rotate it into alignment.
- The hooked (L-shaped) tool may have two sides with equal lengths, or two sides with different lengths.

Notes:

- Like in previous Evals, you can use the PushObject, PullObject, and MoveObject actions to move tools, and the TorqueObject and RotateObject actions to rotate tools. Pushing, Pulling, and Moving one tool into a second tool will cause that second tool to move along with it as you would expect (please note that some bugs for this were fixed in MCS release version 0.7.0).
- Tools may have novel colors/textures applied to them (including, but not limited to, the colors/textures used in Eval 6), but the general shape of the tools will remain the same.

## Passive Agent Tasks

### Passive Agent Overview

- The Passive Agent tasks were designed by CACI's partners at NYU. For more information about these tasks, please see their website: https://www.kanishkgandhi.com/bib
- These are passive/VoE agent tasks. During the evaluation, your system is **required** to call `controller.end_scene()` at the end of each scene with a **continuous** plausibility `rating`, from `0.0` (completely unexpected/surprising) to `1.0` (completely expected/unsurprising). Your system should use the full range of values between `0.0` and `1.0`. Ratings between `0.0` and `1.0` indicate intermediate levels of expectedness/surprise. Your system is not required to also pass a `score`. For more information, please see the documentation here: https://nextcenturycorporation.github.io/MCS/api.html#machine_common_sense.Controller.end_scene
- You begin standing on a platform in the corner of the room, looking down at the room with a three-quarter perspective, and observe a set of eight familiarization (a.k.a. habituation) trials and one test trial. Your VoE (plausibility rating) should be based on the “expectedness” (or “unexpectedness”) of the test trial, based on your system’s prior training and the familiarization trials.
- Goal objects share a common set of colors (azure, brown, chartreuse, cyan, grey, indigo, navy, olive, orange, rose, springgreen, teal, violet, yellow) and shapes (spheres, cylinders, cubes, cones, pyramids, frustums). Agent and non-agent entities share a common set of colors (blue, goldenrod, green, purple) and shapes (blobs).
- All training scenes are either "plausible/expected" or "no expectation". Training scenes also have nine trials, but they aren’t always conceptually separated into “familiarization trials” and “test trials”. Please note that some evaluation tasks have multiple different types of scenes, all of which are described below and labelled appropriately in the datasets.
- Unknown to your systems, all Passive Agent scenes are generated in pairs: an "expected" scene and an "unexpected" scene; an "expected" and a "no-expectation" scene; or an "unexpected" scene and a "no-expectation" scene. After all evaluation scenes are run, our [scoring software](#scoring) compares the ratings returned by the your systems for each pair of scenes; the pair is marked as "correct" in our performance assessment if the correct scene has a higher rating than the other scene.
    - For expected/unexpected pairs, the expected scene should have a higher rating than the unexpected scene.
    - For expected/no-expectation pairs, the expected scene should have a higher rating than the no-expectation scene.
    - For unexpected/no-expectation pairs, the no-expectation scene should have a higher rating than the unexpected scene.

### Passive Agent Data

#### Passive Agent Evaluation Datasets

- Eval 7 dataset (1,000 pairs of each Eval 6 and Eval 7 task): https://eval-7.s3.amazonaws.com/eval_7_passive_agents.zip
- Eval 7 extra data: https://eval-7.s3.amazonaws.com/eval_7_passive_agents_extra.zip
- Eval 6 dataset (includes some older tasks): https://eval-6.s3.amazonaws.com/eval_6_passive_agent.zip
- Eval 5 dataset (includes all tasks designed up to this point): https://eval-5.s3.amazonaws.com/eval_5_passive_agent.zip
- Debug scene files for the MCS scoring software and evaluation UI:
    - Eval 7: https://eval-7.s3.amazonaws.com/eval_7_passive_agents_debug.zip
    - Eval 6: https://eval-6.s3.amazonaws.com/eval_6_passive_agent_debug.zip
    - Eval 5: https://eval-5.s3.amazonaws.com/eval_5_passive_agent_debug.zip
 
#### Passive Agent Training Datasets

The "Single Object" training data is relevant to all Passive Agent tasks. Please see the tasks listed below to find the links to one or more training datasets specific to each task.

##### Single Object Training Data

https://eval-6.s3.amazonaws.com/eval_6_passive_agent_training_single_object.zip

- Each trial shows an agent (A1) approaching a goal object (O1).
- When an agent contacts a goal object, all goal objects are highlighted (color changes to red), as a secondary indication of the successful contact.

TODO VIDEOS

### Passive Agent Tasks Introduced in Evaluation 3

#### Efficient Action (Passive Agent)

Summary:

Passive Agent: Efficient Action tasks require a common-sense understanding of agency. This is a “passive agents” task: you must watch (using only Pass actions) as an agent (blob shape) moves in a grid world over 8 “familiarization” trials and a “test” trial (the world “resets” between each trial using the EndHabituation action). The trials depict the agent approaching an object; in the test trial, some of the obstacles are removed. You must then determine whether the test trial is “expected” (unsurprising) or “unexpected” (surprising) based on whether or not the agent moves in an efficient path (agents should move efficiently).

TODO VIDEOS

##### Efficient Action Training Data

- Time Control: https://eval-5.s3.amazonaws.com/eval_5_passive_agent_efficient_action_time_training_scenes_v2.zip
- Path Control: https://eval-5.s3.amazonaws.com/eval_5_passive_agent_efficient_action_path_training_scenes_v2.zip
- Irrational: https://eval-5.s3.amazonaws.com/eval_5_passive_agent_efficient_action_irrational_training_scenes_v2.zip

#### Object Preference (Passive Agent)

Summary:

Passive Agent: Object Preference tasks require a common-sense understanding of agency. This is a “passive agents” task: you must watch (using only Pass actions) as an agent (blob shape) moves in a grid world over 8 “familiarization” trials and a “test” trial (the world “resets” between each trial using the EndHabituation action). The familizarization trials depict the agent approaching a specific object (the same object in all 8 familiarization trials). You must then determine whether the test trial is “expected” (unsurprising) or “unexpected” (surprising) based on whether or not the agent continued to act with the same preferences it showed during the familiarization trials (approaching the same object).

TODO VIDEOS

##### Object Preference Training Data

https://eval-6.s3.amazonaws.com/eval_6_passive_agent_training_object_preference.zip

- Each trial shows an agent (A1) approaching a goal object (O1), ignoring a second goal object (O2).
- When an agent contacts a goal object, all goal objects are highlighted (color changes to red), as a secondary indication of the successful contact.

### Passive Agent Tasks Introduced in Evaluation 4

#### Inaccessible Goal (Passive Agent)

Summary:

Passive Agent: Inaccessible Goal tasks require a common-sense understanding of agency. This is a “passive agents” task: you must watch (using only Pass actions) as an agent (blob shape) moves in a grid world over 8 “familiarization” trials and a “test” trial (the world “resets” between each trial using the EndHabituation action). The familizarization trials depict the agent retrieving a red triangular "key" object; inserting that key into a "lock" in the green wall, causing the green wall to disappear; and then approaching an "goal" object that was previously blocked by the green wall, but is now accessible. You must then determine whether the test trial is “expected” (unsurprising) or “unexpected” (surprising) based on whether or not the agent used the "key" object when it was necessary to approach the "goal" object (if the "goal" object is not blocked by the green wall, then using the "key" object is unnecessary).

TODO VIDEOS

##### Inaccessible Goal Training Data

https://eval-5.s3.amazonaws.com/eval_5_passive_agent_inaccessible_goal_training_scenes_v2.zip

#### Instrumental Action (Passive Agent)

Summary:

Passive Agent: Instrumental Action tasks require a common-sense understanding of agency. This is a “passive agents” task: you must watch (using only Pass actions) as an agent (blob shape) moves in a grid world over 8 “familiarization” trials and a “test” trial (the world “resets” between each trial using the EndHabituation action). The familizarization trials depict the agent approaching a specific object (the same object in all 8 familiarization trials); in the test trial, obstacles may be moved to block a path to the preferred object. You must then determine whether the test trial is “expected” (unsurprising) or “unexpected” (surprising) based on whether or not the agent can successfully navigate to its preferred object (approaching a different object is unsurprising if the preferred object is blocked).

TODO VIDEOS

##### Instrumental Action Training Data

- Blocking Barriers: https://eval-5.s3.amazonaws.com/eval_5_passive_agent_instrumental_action_blocking_barriers_training_scenes_v2.zip
- Inconsequential Barriers: https://eval-5.s3.amazonaws.com/eval_5_passive_agent_instrumental_action_inconsequential_barriers_training_scenes_v2.zip
- No Barriers: https://eval-5.s3.amazonaws.com/eval_5_passive_agent_instrumental_action_no_barriers_training_scenes_v2.zip

#### Multiple Agents (Passive Agent)

Summary:

Passive Agent: Multiple Agents tasks require a common-sense understanding of agency. This is a “passive agents” task: you must watch (using only Pass actions) as an agent (blob shape) moves in a grid world over 8 “familiarization” trials and a “test” trial (the world “resets” between each trial using the EndHabituation action). The familizarization trials depict the agent approaching a specific object (the same object in all 8 familiarization trials); in the test trial, either the same agent or a new agent will approach a different object. You must then determine whether the test trial is “more expected” (unsurprising) or “more unexpected” (surprising) based on whether or not the agent with a known preference approached a different object (it is unsurprising for a new agent to have a different preference).

TODO VIDEOS

##### Multiple Agents Training Data

https://eval-6.s3.amazonaws.com/eval_6_passive_agent_training_multiple_agents.zip

- Each trial shows an agent (either A1 or A2) approaching a goal object (O1).
- The same object (O1) appears in each trial, but only one of the two agents (A1, A2).
- When an agent contacts a goal object, all goal objects are highlighted (color changes to red), as a secondary indication of the successful contact.
- In the evaluation data, multiple goal objects will appear in each trial, and the different agents may have different preferences.

### Passive Agent Tasks Introduced in Evaluation 6

#### Agent / Non-Agent (Passive Agent)

Summary:

Passive Agent: Agent/Non-Agent tasks require a common-sense understanding of agency. This is a “passive agents” task: you must watch (using only Pass actions) as an ambiguous agent-like entity (blob shape) moves in a grid world over 8 “familiarization” trials and a “test” trial (the world “resets” between each trial using the EndHabituation action). The familiarization trials depict the entity approaching a specific object (the same object in all 8 familiarization trials). The entity is either an agent or a non-agent: agents move autonomously, while non-agents are moved because they are hit by the spinning “paddle”. You must then determine whether the test trial is “more expected” (unsurprising) or “more unexpected” (surprising) based on how the entity acts: if the entity is an agent, it should continue to act with the same preferences it showed during the familiarization trials (approaching the same object); if the entity is a non-agent, then it doesn’t have preferences, because its movement is controlled by the paddle, so it’s just as likely to approach either object.

Details:

- All of these scenes (except "Collect" training scenes) have a “paddle” (black wall, consistent height) and an “occluder” (white wall, differing height). The paddle is a mechanism that is constantly spinning and does not have agency. The occluder can be seen “out-of-the-way” for the first eight trials, but then is randomly positioned “in-the-way” for the ninth trial, partially blocking your view of what is happening.
- All of these scenes have either an “agent” or a “non-agent”. Since the agent and the non-agent share the same set of colors and “blob” models, your system must observe their behavior to differentiate them during the evaluation: specifically, agents have agency and preferences.
- If an agent shows a preference for a specific goal object during the familiarization trials (by approaching the goal object), it is expected/plausible for the agent to show the same preference (for the same goal object) during the test trial, and unexpected/implausible for the agent to show a different preference (for a different goal object). As in previous evaluations, your system should return a plausibility / expectedness rating that’s very high for “expected” scenes (1.0 = definitely expected) and very low for “unexpected” scenes (0.0 = definitely unexpected).
- If a non-agent shows a “preference” for a specific goal object during the familiarization trials (by “approaching” the goal object, after being hit by the paddle), then there is no expectation for the non-agent to show either the same preference or a different preference, because it does not have agency. For “no expectation” scenes, your system should return a plausibility / expectedness rating that’s lower than for “expected” scenes but higher than for “unexpected” scenes.

Example Evaluation Scenes:

TODO VIDEOS

##### Agent / Non-Agent Training Data

https://eval-6.s3.amazonaws.com/eval_6_passive_agent_training_agent_nonagent_tasks.zip

Agent One Goal Training Data:

- Each trial shows an agent (A1) approaching a goal object (O1).
- When an agent contacts a goal object, all goal objects are highlighted (color changes to red), as a secondary indication of the successful contact.
- The agent and the paddle do not come into contact. (The agent has agency and can move itself.)

TODO VIDEOS

Agent Preference Training Data:

- Each trial shows an agent (A1) approaching a goal object (O1), ignoring a second goal object (O2).
- When an agent contacts a goal object, all goal objects are highlighted (color changes to red), as a secondary indication of the successful contact.
- The agent and the paddle do not come into contact. (The agent has agency and can move itself.)

TODO VIDEOS

Collect Training Data:

- Each trial shows an agent (A1) approaching a goal object (O1). Similar to the Single Object dataset (see above).
- When an agent contacts a goal object, all goal objects are highlighted (color changes to red), as a secondary indication of the successful contact.
- No paddle or occluder.

TODO VIDEOS

Non-Agent One Goal Training Data:

- Each trial shows a non-agent (N1) being hit by the paddle in a realistic direction and stopping when it contacts a goal object (O1) or a wall.
- When a non-agent contacts a goal object, all goal objects are highlighted (color changes to red), as a secondary indication of the successful contact.
- While the non-agent (N1) sometimes contacts the goal object (O1) in these trials, it cannot control its own movement, because it does not have agency.

TODO VIDEOS

Non-Agent "Preference" Training Data:

- Each trial shows a non-agent (N1) being hit by the paddle in a realistic direction and stopping when it contacts a goal object (O1), ignore a second goal object (O2).
- When a non-agent contacts a goal object, all goal objects are highlighted (color changes to red), as a secondary indication of the successful contact.
- While the non-agent (N1) always contacts the goal object (O1) in these trials, it cannot control its own movement, because it does not have agency.

TODO VIDEOS

#### Social and Instrumental Approach and Imitation (Passive Agent)

Summary:

Passive Agent: Appraoch and Imitation tasks require a common-sense understanding of agency. This is a “passive agents” task: you must watch (using only Pass actions) as three agents (blob shapes) move in a grid world over 8 “familiarization” trials and a “test” trial (the world “resets” between each trial using the EndHabituation action). 

In the Approach tasks, the familiarization trials depict an agent approaching another specific agent (the same agent in all 8 familiarization trials). You must then determine whether the test trial is “expected” (unsurprising) or “unexpected” (surprising) based on whether or not the agent continued to act with the same preferences it showed during the familiarization trials (imitating the movement pattern of the other agent it approached).

In the Imitation tasks, the familiarization trials depict the three agents moving in specific patterns, which are consistent across all 8 trials; two of the agents always have the same movement pattern. You must then determine whether the test trial is “expected” (unsurprising) or “unexpected” (surprising) based on whether or not the agent continued to act with the same preferences it showed during the familiarization trials (approaching the other agent who had the same movement pattern).

Details:

- All of these scenes have three agents with different shapes and colors: two agents move in different patterns (like an L-shape and a C-shape), and a third agent imitates one of the first two agents by moving in the same pattern as that agent.
- The “Social Approach” category shows an agent approaching another agent, and then imitating it. The “Social Imitation” category shows an agent imitating another agent, and then approaching it. If an agent shows a preference for another agent during the familiarization trials (by approaching or imitating that agent), it is expected/plausible for the agent to show the same preference (by approaching or imitating the same agent) during the test trial, and unexpected/implausible for the agent to show a different preference (by approaching or imitating a different agent). As in previous evaluations, your system should return a plausibility / expectedness rating that’s very high for “expected” scenes (1.0 = definitely expected) and very low for “unexpected” scenes (0.0 = definitely unexpected).
- The “Instrumental Approach” and “Instrumental Imitation” categories introduce a goal object that the agent contacts while imitating a movement pattern. If an agent appears to show a preference for another agent (by approaching or imitating that agent), but simultaneously contacts a goal object, then there is no expectation for that agent to show either the same preference or a different preference, because it is impossible to know whether the agent is trying to imitate another agent or contact the goal object. For “no expectation” scenes, your system should return a plausibility / expectedness rating that’s lower than for “expected” scenes but higher than for “unexpected” scenes.

Example Evaluation Scenes:

TODO VIDEOS

##### Social and Instrumental Approach and Imitation Training Data

https://eval-6.s3.amazonaws.com/eval_6_passive_agent_training_approach_imitation_tasks.zip

Social Approach:

- Each trial shows three agents (A1, A2, A3).
- Each familiarization trial shows agent A1 approaching agent A2, ignoring agent A3.
- The test trial shows agent A2 and agent A3 moving in a different pattern, and then agent A1 moving in the same pattern as agent A2.

TODO VIDEOS

Instrumental Approach:

- Like Social Approach (see above), but when agent A1 moves during the test trial, it contacts a goal object (O1) while moving in its pattern.
- When an agent contacts a goal object, all goal objects are highlighted (color changes to red), as a secondary indication of the successful contact.

TODO VIDEOS

Social Imitation:

- Each trial shows three agents (A1, A2, A3).
- Each familiarization trial shows either agent A1 or agent A2 moving in a different pattern, and then agent A3 moving in the same pattern as either agent A1 or agent A2.
- Agent A1’s movement pattern never changes across trials (assuming it moves during that trial). The same is true for agent A2’s and agent A3’s movement patterns.
- The test trial shows agent A3 approaching the other agent (either A1 or A2) who has the same movement pattern.

TODO VIDEOS

Instrumental Imitation:

- Like Social Imitation (see above), but when agent A3 moves, it contacts a goal object (O1) while moving in its pattern.
- Unlike Social Imitation, the test trial shows agent A3 approach goal object O1 rather than another agent.
- When an agent contacts a goal object, all goal objects are highlighted (color changes to red), as a secondary indication of the successful contact.
- Some trials show agent A3 contacting goal object O1 multiple times. When an agent contacts a goal object a second time, its highlight is deactivated (color changes back to original color).

TODO VIDEOS

### Passive Agent Tasks Introduced in Evaluation 7

#### Helper / Hinderer (Passive Agent)

Details:

- All of these trials have one inanimate object and three agents (blobs): the primary agent tries to approach the inanimate object, and the other two agents either “help” or “hinder” the primary agent attain its goal.
- Some trials include a blue occluder that is moved by the “helper” agent or “hinderer” agent: the “helper” agent moves the blue occluder to unobstruct the primary agent’s path to the object; the “hinderer” agent moves the blue occluder to obstruct the primary agent’s path to the object.
- The test trial does not show the inanimate object or blue occluder; instead, it shows the primary agent approaching one of the other two agents (indicating a preference for that agent). It is expected / plausible for the primary agent to prefer the “helper” agent (the agent who unobstructed its path during the familiarization trials), and unexpected / implausible to prefer the “hinderer” agent (the agent who obstructed its path during the familiarization trials). As in previous evaluations, your system should return a plausibility / expectedness rating that’s very high for “expected” scenes (1.0 = definitely expected) and very low for “unexpected” scenes (0.0 = definitely unexpected).

##### Helper / Hinderer Training Data

https://eval-7.s3.amazonaws.com/passive_agent_training_helper_hinderer.zip

Differences from evaluation tasks: In the training data, the primary agent starts in one of the two smaller areas, and the inanimate object starts in the bigger area; in the evaluation data, the primary agent starts in the bigger area, and the inanimate object starts in one of the two smaller areas.

TODO VIDEOS

#### True / False Belief (Passive Agent)

Details:

All of these trials have one inanimate object and two agents (blobs): the primary agent tries to approach the inanimate object, and the secondary agent (which is only present during the test trial) moves the inanimate object. The inanimate object is always positioned behind one of the two white occluders during the test trial, and during some of the familiarization trials as well; the primary agent cannot see the inanimate object from its starting position while the object is positioned behind an occluder (though the TA1 agent may be able to see it).
- In True Belief tasks, the primary agent is present (and can see everything happen) while the secondary agent moves the inanimate object from its position hidden behind one occluder to a new position behind a second occluder. It is expected / plausible for the primary agent to approach the new position of the object, behind the second occluder (since it saw the secondary agent move the object to that position), and unexpected / implausible for the primary agent to approach the old position of the object, behind the original occluder.
- In False Belief tasks, the primary agent is NOT present (and does not see anything) while the secondary agent moves the inanimate object from its position hidden behind one occluder to a new position behind a second occluder. It is expected / plausible for the primary agent to approach the old position of the object, behind the original occluder (since it did not see the secondary agent move the object to a new position), and unexpected / implausible for the primary agent to approach the new position of the object, behind the second occluder.
- As in previous evaluations, your system should return a plausibility / expectedness rating that’s very high for “expected” scenes (1.0 = definitely expected) and very low for “unexpected” scenes (0.0 = definitely unexpected).

##### True / False Belief Training Data

- True Belief training data: https://eval-7.s3.amazonaws.com/passive_agent_training_true_belief.zip
- False Belief training data: https://eval-7.s3.amazonaws.com/passive_agent_training_false_belief.zip

Differences from evaluation tasks: In the training data, the secondary agent moves the inanimate object to a new position behind the same occluder; in the evaluation data, the secondary agent moves the inanimate object to a new position behind the other occluder.

TODO VIDEOS

## Passive Physics Tasks

### Passive Physics Overview

Each trial, or "scene", for a passive physics task occurs within a procedurally generated room in our 3D environment. Each passive physics task requires that you use common-sense reasoning of the laws of physics to categorize a scene as either "plausible" or "implausible". Your system will be forced to only use "Pass" actions during the entirety of the scene, and must then return a **binary plausibility rating** and a **continuous plausibility score** to the MCS python library (see below). Even though these tasks seem different from the interactive tasks, they are run within the same 3D environment as the interactive tasks, and objects behave (roll, fall, bounce, etc.) in the same way (except for implausible events).

- Binary plausibility ratings evaluate the event as a whole after it has concluded (either “implausible” or “plausible”). We use these binary ratings to compute sensitivity scores such as d'. We will not attempt to derive binary scores from continuous scores, because we do not want to assume where each system places the threshold for concluding a scene is implausible.
- Continuous plausibility scores evaluate the event as a whole after it has concluded, between 0 (completely implausible) and 1 (completely plausible). These scores can be used to compute ROC curves and AOCs to characterize performance on the scene. This is one of the ways that we can compare performance - not only across performers, but across conditions (e.g. scenes containing familiar objects vs. scenes containing novel objects). We anticipate that some events will not be clearly 100% plausible or implausible, even to a very high performing algorithm. The ideal outcome is for the AI system to recognize that one outcome was more expected than another. Continuous scores support that kind of comparison better than binary scores.

### Passive Physics Data

TODO DOWNLOAD

Training scenes for the following tasks can be made using the ILE Scene Generator: https://github.com/NextCenturyCorporation/mcs-scene-generator/

### Passive Physics Tasks Introduced in Evaluation 3

#### Object Permanence (Passive Physics)

Summary:

Object Permanence tasks require a common-sense understanding of object permanence. This is a “passive physics” task: you must watch objects moving in a scene (using only Pass actions) and determine whether the simulation was “plausible” (realistic) or “implausible” (unrealistic) based on whether or not objects spontaneously appear and/or disappear.

TODO VIDEOS

#### Shape Constancy (Passive Physics)

Summary:

Shape Constancy tasks require a common-sense understanding of shape constancy. This is a “passive physics” task: you must watch objects moving in a scene (using only Pass actions) and determine whether the simulation was “plausible” (realistic) or “implausible” (unrealistic) based on whether or not objects spontaneously transform into different shapes.

TODO VIDEOS

#### Spatio-Temporal Continuity (Passive Physics)

Summary:

Spatio-Temporal Continuity tasks require a common-sense understanding of spatial and temporal continuity. This is a “passive physics” task: you must watch objects moving a scene (using only Pass actions) and determine whether the simulation was “plausible” (realistic) or “implausible” (unrealistic) based on whether or not objects spontaneously teleport across the room.

TODO VIDEOS

### Passive Physics Tasks Introduced in Evaluation 3.5

#### Gravity Support (Passive Physics)

Summary:

Passive Gravity Support tasks require a common-sense understanding of gravity. This is a “passive physics” task: you must watch objects moving in a scene (using only Pass actions) and determine whether the simulation was “plausible” (realistic) or “implausible” (unrealistic) based on whether or not objects are properly supported.

|||||
|---|---|---|---|
![gravity_support_ex_01](https://github.com/NextCenturyCorporation/MCS/assets/10994382/568c3ba3-f357-44af-b740-1811d3fc9d99) | ![gravity_support_ex_02](https://github.com/NextCenturyCorporation/MCS/assets/10994382/2254e21c-7e19-4076-812f-c1a4f26cb24c) | ![gravity_support_ex_03](https://github.com/NextCenturyCorporation/MCS/assets/10994382/8eef0960-6cce-4976-a819-b3e2a807668a) | ![gravity_support_ex_04](https://github.com/NextCenturyCorporation/MCS/assets/10994382/5fad4cc8-65cf-47fa-806c-64f2cada4f24)
![gravity_support_ex_05](https://github.com/NextCenturyCorporation/MCS/assets/10994382/f6b3cc0a-8368-4613-ac1d-675fcca03d42) | ![gravity_support_ex_06](https://github.com/NextCenturyCorporation/MCS/assets/10994382/6b81d66a-3b2f-473c-9afc-4e9960055be4) | ![gravity_support_ex_07](https://github.com/NextCenturyCorporation/MCS/assets/10994382/8ad20113-d922-4acb-b062-6ac360300d55) | ![gravity_support_ex_08](https://github.com/NextCenturyCorporation/MCS/assets/10994382/7336d2f3-6e1e-4b45-abfe-17fbb72d740a)
![gravity_support_ex_09](https://github.com/NextCenturyCorporation/MCS/assets/10994382/6e80e487-8c0e-4fe1-adba-c8e0d13651e5) | ![gravity_support_ex_10](https://github.com/NextCenturyCorporation/MCS/assets/10994382/3b0d6c27-71f1-4f67-b26e-64640920228f) | ![gravity_support_ex_11](https://github.com/NextCenturyCorporation/MCS/assets/10994382/135e8da0-1c23-43fd-9b8e-4e4b9e25fa5f) | ![gravity_support_ex_12](https://github.com/NextCenturyCorporation/MCS/assets/10994382/26284069-4582-4448-ba12-8a7184f10a92)

### Passive Physics Tasks Introduced in Evaluation 4

#### Collisions (Passive Physics)

Summary:

Passive Collision tasks require a common-sense understanding of collision physics. This is a “passive physics” task: you must watch objects moving in a scene (using only Pass actions) and determine whether the simulation was “plausible” (realistic) or “implausible” (unrealistic) based on whether or not objects properly collide with one another.

TODO VIDEOS

## Other Tasks

### Other Data

TODO DOWNLOAD

Training scenes for the following tasks can be made using the ILE Scene Generator: https://github.com/NextCenturyCorporation/mcs-scene-generator/

### Other Tasks Introduced in Evaluation 6

#### Seeing Leads to Knowing (Passive)

Summary:

Seeing Leads to Knowing tasks require a common-sense understanding of agency. This is a “passive” task: you must watch (using only Pass actions) as a soccer ball is deposited into a container and an agent approaches a container, and then determine whether the simulation was “plausible” (realistic) or “implausible” (unrealistic) based on whether or not the agent acted with common-sense reasoning (if the agent saw the ball being deposited, it should approach the container holding the ball; otherwise it should approach one of the containers behind it, because one of those containers holds the ball).

Plausible:

https://github.com/NextCenturyCorporation/MCS/assets/10994382/a3c4a8b0-9c3f-4580-a9a3-7ee26fec66ce

Plausible:

https://github.com/NextCenturyCorporation/MCS/assets/10994382/fcdbc37f-c616-407d-b312-ff4f082d5a8c

Implausible:

https://github.com/NextCenturyCorporation/MCS/assets/10994382/90f065bb-3776-4112-99f3-b060bd525a36

Implausible:

https://github.com/NextCenturyCorporation/MCS/assets/10994382/8a7c0e7e-275b-42a3-b2c8-6ea43ab251da

Details:

- This is a passive/VoE task. Similar to the passive physics tasks, your system is expected to return a binary plausibility rating of either "plausible" or "implausible" as well as a continuous plausibility score between 0.0 (completely implausible) and 1.0 (completely plausible).
- You start in a room looking at four identical open-topped containers. An agent immediately walks into view and stands in the middle of the room, looking at two of the containers. Then four placers simultaneously descend from the ceiling, one over each container. One placer is holding the target (soccer ball) and drops it into a container; the other three placers are not holding anything, but change color/state like the first placer. The agent then approaches the container it believes is holding the target. You must determine whether the agent's choice is plausible or implausible based on what the agent is able to see.
- If the target is dropped into one of the two containers in front of the agent (which it can see), then it is plausible for the agent to approach that specific container, and implausible for the agent to approach a different container.
- If the target is dropped into one of the two containers behind the agent (which it cannot see), then it is plausible for the agent to approach either of the two containers behind it, and implausible for the agent to approach either of the two containers in front of it.
- The containers are always in the same locations, but may vary slightly in shape, size, and color.
- The agent can enter from either the left side or the right side of your view.

Notes:

- Seeing Leads to Knowing scenes use the new "passive" goal category to differentiate them from other passive scenes. For more information on "passive" goals, please see our API doc here: https://nextcenturycorporation.github.io/MCS/api.html#machine_common_sense.GoalCategory.PASSIVE
- Your system's binary plausibility rating and continuous plausibility score must be included when calling the "end_scene" function. For more information on "end_scene", please see our API doc here: https://nextcenturycorporation.github.io/MCS/api.html#machine_common_sense.Controller.end_scene
- Your starting position and viewing angle will remain consistent across all Seeing Leads to Knowing scenes.
- As with our other passive tasks, we expect that you will train your systems using only plausible Seeing Leads to Knowing data, to mimic the "training" of human babies who only experience plausible scenarios. Because of this, the ILE Scene Generator is only designed to create plausible Seeing Leads to Knowing scenes for your training. We have provided a few example implausible scenes (see above) for you to see how they will look.

## Evaluation

Running of evaluation scenes is done by our `mcs-pipeline` software: https://github.com/NextCenturyCorporation/mcs-pipeline

Please note that all scenes are run during the evaluation using **metadata level 2**.

## Scoring

Scoring of evaluation scenes is done by our `mcs-ingest` software: https://github.com/NextCenturyCorporation/mcs-ingest

Please note that Interactive and Passive tasks are scored differently; see the Task sections above for more information.

### Ambiguous and Control Trials

Some scenes (particularly Interactive "forced choice" scenes) are intentionally ambiguous: the soccer ball can reasonably be hidden in multiple places.

Some scenes (particularly Interactive scenes) are control trials: the trial is not actually testing the common sense concept for the task, and successfully retrieving the soccer ball requires little or no common sense reasoning.

Your system's success in these scenes is not factored into your quantitative evaluation score, but will be reviewed as part of our qualitative analysis of your evaluation results.

### Scorecard

Some behaviors are not obviously wrong, but seem to lack common-sense, and are thus noteworthy. Examples include repeatedly trying failed actions and ignoring a goal object when it is easily accessible (in sight and unobstructed). These actions are recorded as part of our "scorecard" metrics. The scorecard is not factored into your quantitative evaluation score, but will be reviewed as part of our qualitative analysis of your evaluation results. For a full list of our scorecard metrics, please see this page: https://github.com/NextCenturyCorporation/mcs-ingest/blob/master/scorecard/README.md

## Acknowledgements

This material is based upon work supported by the Defense Advanced Research Projects Agency (DARPA) and Naval Information Warfare Center, Pacific (NIWC Pacific) under Contract No. N6600119C4030. Any opinions, findings and conclusions or recommendations expressed in this material are those of the author(s) and do not necessarily reflect the views of the DARPA or NIWC Pacific.

## License

Code in this repository is made available by CACI (formerly Next Century Corporation) under the Apache 2 Open Source License. You may freely download, use, and modify, in whole or in part, the source code or release packages. Any restrictions or attribution requirements are spelled out in the license file. For more information about the Apache license, please visit the The Apache Software Foundation’s License FAQ.

Copyright 2023 CACI (formerly Next Century Corporation)
