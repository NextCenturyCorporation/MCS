from enum import Enum, unique


@unique
class TaskDescription(Enum):
    """
    The names for each enum correspond to the naming conventions currently
    followed by all scenes checked into the webenabled/scenes directory.
    Please note that any scenes not matching the naming conventions in this
    file will likely not have their task description found to display in the
    UI.
    """

    # Interactive Tasks (in alphabetical order)
    INTERACTIVE_AGENT_IDENTIFICATION = (
        "Agent Identification tasks require a common-sense understanding of "
        "agency. You must identify the agent, approach it, use "
        "InteractWithAgent on the agent to request the soccer ball, and then"
        " use PickupObject on the ball once the agent produces it which "
        "completes the scenario. This is a \"forced choice\" task: "
        "once you walk off the platform onto one side of the room, "
        "you are unable to move to the other side of the room."
    )

    INTERACTIVE_ARITHMETIC = (
        "Arithmetic tasks require a common-sense understanding of addition "
        "and subtraction. This is a \"forced choice\" task: once you walk off "
        "the platform onto one side of the room, you are unable to move to "
        "the other side of the room. You must watch (using the Pass action) "
        "as zero or more soccer balls are added to or subtracted from each "
        "side of the room. Then you must identify which side of the room has"
        " the most reachable soccer balls and use PickupObject on each of "
        "them to pick them up which completes the scenario. Sometimes the "
        "addition/subtraction is occluded so you have to remember how many "
        "balls were added to or subtracted from each side."
    )

    INTERACTIVE_ASYMMETRIC_TOOL_USE = (
        "Asymmetric Tool Use tasks require a common-sense understanding of "
        "affordances. You must use an asymmetric \"tool\" (a large L-shaped "
        "object with wheels and a unique texture) to extract the soccer ball "
        "from the middle of a pool of lava (using PullObject or MoveObject to "
        "pull the tool so it collides with the ball causing it to roll out "
        "from the lava), and then use PickupObject on the ball, which "
        "completes the scenario. Sometimes the tool must be rotated (using "
        "RotateObject or TorqueObject) before it is pulled."
    )

    INTERACTIVE_COLLISIONS = (
        "Interactive Collision tasks require a common-sense understanding "
        "of trajectory and collision. You must watch (using the Pass action) "
        "as a green \"shooter ball\" is launched across the floor toward a "
        "stationary soccer ball, but you do not see the entire trajectory "
        "(and, sometimes, even the collision itself), due to a large "
        "occluding wall which descends in front of you; you must then "
        "determine which side of the room contains the soccer ball, "
        "find it, and use PickupObject on it to pick it up, which completes "
        "the scenario. To access a side of the room, you must open one of "
        "the doors (using the OpenObject action) in the occluding wall. "
        "This is a \"forced choice\" task: once you open the door to one "
        "side of the room, you are unable to access the other side of the "
        "room (because it is blocked by lava)."
    )

    INTERACTIVE_CONTAINERS = (
        "Container Retrieval tasks require a common-sense understanding "
        "of containment. You must find the soccer ball, which may or may "
        "not be hidden inside a container (use OpenObject to open a "
        "closed container), and then use PickupObject on the ball to pick "
        "it up."
    )

    INTERACTIVE_HOLES = (
        "Hole Navigation tasks require a common-sense understanding of "
        "navigation in a dangerous environment. You must walk through a "
        "room full of holes in order to find the soccer ball, and then use "
        "PickupObject on the ball to pick it up, which completes the "
        "scenario. Walking into a hole will make it impossible to reach "
        "the ball (you fall in and cannot escape). Sometimes the ball "
        "is on the floor, and sometimes an agent is holding the ball "
        "instead (use InteractWithAgent on the agent to request the "
        "soccer ball)."
    )

    INTERACTIVE_IMITATION = (
        "Interactive Imitation tasks require a common-sense understanding "
        "of agency. You must watch (using the Pass action) as an agent "
        "performs a series of actions (opening one or more chests in a "
        "specific order) in order to access a soccer ball; then the room "
        "is \"reset\" (using the EndHabituation action) and you must perform "
        "the same actions in the same order (using the OpenObject action on "
        "the correct chests). Then you will be able to reach the soccer "
        "ball, and you can use PickupObject on it to pick it up, which "
        "completes the scenario. Performing the wrong actions (opening the "
        "wrong chests, or opening them in the wrong order) automatically "
        "fails the scenario. Sometimes you or the chests are repositioned "
        "when the room is reset."
    )

    INTERACTIVE_LAVA = (
        "Lava Navigation tasks require a common-sense understanding of "
        "navigation in a dangerous environment. You must walk through a room "
        "full of lava in order to find the soccer ball, and then use "
        "PickupObject on the ball to pick it up, which completes the "
        "scenario. Walking into the lava immediately ends the scene "
        "(therefore failing the scenario). Sometimes the ball is on the "
        "floor, and sometimes an agent is holding the ball instead "
        "(use InteractWithAgent on the agent to request the soccer ball)."
    )

    INTERACTIVE_MOVING_TARGET_PREDICTION = (
        "Moving Target Prediction tasks require a common-sense understanding"
        " of trajectory. You are in a room with lava on both sides and a"
        " \"safe zone\" in the center. After spinning around to see the "
        "entire room (using the RotateRight action), you watch (using "
        "the Pass action) as a soccer ball is launched across the floor, "
        "toward the \"safe zone\". You must move to intercept the ball and "
        "use PickupObject on it before it rolls into the lava and out of "
        "your reach. Walking into the lava immediately ends the scene "
        "(therefore failing the scenario)."
    )

    INTERACTIVE_NUMBER_COMPARISON = (
        "Number Comparison tasks require a common-sense understanding of "
        "numbers. This is a \"forced choice\" task: once you walk off the "
        "platform onto one side of the room, you are unable to move to the "
        "other side of the room. You must identify which side of the room "
        "has the most soccer balls and use PickupObject on each of them to "
        "pick them up which completes the scenario. Sometimes the balls "
        "become occluded so you have to remember how many were originally "
        "present on each side."
    )

    INTERACTIVE_OBJECT_PERMANENCE = (
        "Interactive Object Permanence tasks require a common-sense "
        "understanding of object permanence. You must watch (using the Pass "
        "action) as a soccer ball is tossed through the air and lands hidden "
        "behind an occluder; you must then determine which side of the room "
        "contains the ball, find it, and use PickupObject on it, which "
        "completes the scenario. This is a \"forced choice\" task: once you "
        "walk off the platform onto one side of the room, you are unable "
        "to move to the other side of the room."
    )

    INTERACTIVE_OBSTACLES = (
        "Obstacle Retrieval tasks require a common-sense understanding of "
        "occlusion. You must find the soccer ball, which may or may not be "
        "hidden behind \"obstacle\" furniture (furniture which you can see "
        "through, but cannot walk through), and then use PickupObject on "
        "the ball to pick it up, which completes the scenario."
    )

    INTERACTIVE_OCCLUDERS = (
        "Occluder Retrieval tasks require a common-sense understanding of "
        "occlusion. You must find the soccer ball, which may or may not be "
        "hidden behind occluding furniture (furniture which you can neither "
        "see through nor walk through), and then use PickupObject on the "
        "ball to pick it up, which completes the scenario."
    )

    INTERACTIVE_RAMPS = (
        "Ramp Navigation tasks require a common-sense understanding of "
        "navigation in an environment with multiple stories. You must walk "
        "up and/or down one or more ramps in order to find the soccer ball, "
        "and then use PickupObject on the ball to pick it up, which "
        "completes the scenario. Sometimes the ball is on the floor, and "
        "sometimes an agent is holding the ball instead (use "
        "InteractWithAgent on the agent to request the soccer ball)."
    )

    INTERACTIVE_SET_ROTATION = (
        "Set Rotation tasks require a common-sense understanding of tracking "
        "objects as they move. You must watch (using the Pass action) as a "
        "soccer ball is deposited into one of the containers in the room, "
        "and lids are placed on all of the containers. Then either you will "
        "continue watching as the \"turntable\" (the large grey cog) rotates,"
        " or you will be forced to partially (or fully) circumnavigate the "
        "turntable using a series of Move and Rotate actions. You must "
        "identify which container holds the soccer ball, approach it, use "
        "OpenObject on it to open it, and then use PickupObject on the "
        "ball to pick it up, which completes the scenario. This is a "
        "\"forced choice\" task: once you open one container, you are "
        "unable to open other containers."
    )

    INTERACTIVE_SHELL_GAME = (
        "Shell Game tasks require a common-sense understanding of tracking "
        "objects as they move. You must watch (using the Pass action) as a "
        "soccer ball is deposited into one of the containers in the room, "
        "and lids are placed on all of the containers, then poles will "
        "descend from the ceiling and move one or more of the containers "
        "to new locations. You must identify which container holds the soccer"
        " ball, approach it, use OpenObject on it to open it, and then use "
        "PickupObject on the ball to pick it up, which completes the "
        "scenario. This is a \"forced choice\" task: once you open one "
        "container, you are unable to open other containers. Please note "
        "that sometimes the containers are moved before the soccer ball is "
        "deposited."
    )

    INTERACTIVE_SOLIDITY = (
        "Solidity tasks require a common-sense understanding of objects and"
        " gravity. You must watch (using the Pass action) as a soccer ball "
        "is lowered by a pole, but the ball is hidden as it goes behind a "
        "large occluding wall before you see the pole release it; you must "
        "then determine which side of the room contains the ball, find it, "
        "and use PickupObject on it to pick it up, which completes the "
        "scenario. To access a part of the room, you must open one of the "
        "doors (using the OpenObject action) in the occluding wall: the "
        "left side of the room can be accessed using the left door; the "
        "right side of the room can be accessed using the right door; and "
        "the platform can be accessed using the middle door. This is a "
        "\"forced choice\" task: once you open the door to one part of "
        "the room, you are unable to access the other parts of the room."
    )

    INTERACTIVE_SPATIAL_ELIMINATION = (
        "Spatial Elimination tasks require a common-sense understanding of"
        " spatial elimination. This is a \"forced choice\" task: once you "
        "walk off the platform onto one side of the room, you are unable to "
        "move to the other side of the room. You must identify which side of "
        "the room has the soccer ball, find it, and then use PickupObject on "
        "the ball to pick it up, which completes the scenario."
    )

    INTERACTIVE_SPATIAL_REFERENCE = (
        "Spatial Reference tasks require a common-sense understanding of "
        "agency. You must watch (using the Pass action) as both an agent "
        "and a \"blob\" move and \"point\" to a container on one side of the "
        "room. You must use the agent's point (and ignore the blob) to "
        "determine which container holds the soccer ball, approach it, use "
        "OpenObject to open it, and then use PickupObject on the ball to "
        "pick it up, which completes the scenario. This is a "
        "\"forced choice\" task: once you walk off the platform onto one "
        "side of the room, you are unable to move to the other side of "
        "the room. Agents can be identified by their facial features "
        "(blobs don't have faces) and their autonomous movement (blobs "
        "\"move\" by rotating on turntables)."
    )

    INTERACTIVE_SPATIAL_REORIENTATION = (
        "Spatial Reorientation tasks require a common-sense understanding "
        "of spatial landmarks. After spinning around to see the entire room "
        "(using the RotateRight action), you must watch (using the Pass "
        "action) as a soccer ball is deposited into a container on one "
        "side of the room; then you are \"kidnapped\" (using the "
        "EndHabituation action) and either kept on the same side of the "
        "room or moved to the opposite side. You must use landmarks "
        "(sometimes the room has a trapezoidal shape, a "
        "differently-colored wall, or a piece of furniture) to identify "
        "which side of the room has the soccer ball, find it, and then "
        "use PickupObject on the ball to pick it up, which completes "
        "the scenario. This is a \"forced choice\" task: once you walk "
        "off the platform onto one side of the room, you are unable to "
        "move to the other side of the room."
    )

    INTERACTIVE_SUPPORT_RELATIONS = (
        "Interactive Gravity Support Relations tasks require a common-sense"
        " understanding of gravity. You must watch (using the Pass action) "
        "as a \"container\" holding a soccer ball is lowered by poles, but "
        "the container and the ball are hidden as they go behind a large "
        "occluding wall before you see the poles release them; you must "
        "then determine which side of the room contains the ball, find it,"
        " and use PickupObject on it to pick it up, which completes the "
        "scenario. The container is sometimes released fully onto the "
        "platform, fully onto the floor, or partially onto the platform, "
        "and possibly falling onto the floor. To access a part of the room, "
        "you must open one of the doors (using the OpenObject action) in "
        "the occluding wall: the left side of the room can be accessed "
        "using the left door; the right side of the room can be accessed "
        "using the right door; and the platform can be accessed using the "
        "middle door. This is a \"forced choice\" task: once you open the "
        "door to one part of the room, you are unable to access the other "
        "parts of the room."
    )

    INTERACTIVE_SYMMETRIC_TOOL_USE = (
        "Symmetric Tool Use tasks require a common-sense understanding of "
        "affordances. You must use a symmetric \"tool\" (a large rectangular "
        "object with wheels and a unique texture) to extract the soccer ball "
        "from the middle of a pool of lava (using PushObject or MoveObject "
        "to push the tool so it collides with the ball causing it to roll "
        "out from the lava), and then use PickupObject on the ball, which "
        "completes the scenario."
    )

    INTERACTIVE_TOOL_CHOICE = (
        "Tool Choice tasks require a common-sense understanding of "
        "affordances. Like the Symmetric Tool Use task, you must use a "
        "symmetric \"tool\" (a large rectangular object with wheels and a "
        "unique texture) to extract the soccer ball from the middle of a "
        "pool of lava (using PushObject or MoveObject to push the tool so "
        "it collides with the ball causing it to roll out from the lava), "
        "and then use PickupObject on the ball and complete the scenario. "
        "Sometimes the tool must be rotated (using RotateObject or "
        "TorqueObject) before it is pushed. This is a \"forced choice\" "
        "task: once you walk off the platform onto one side of the room, "
        "you are unable to move to the other side of the room. One side of "
        "the room contains a tool that can be used successfully to retrieve "
        "the soccer ball, while the other side contains a tool that is "
        "broken, inaccessible, or not a useful size."
    )

    INTERACTIVE_TRAJECTORY = (
        "Occluded Trajectory tasks require a common-sense understanding of"
        " trajectory. You must watch (using the Pass action) as a soccer "
        "ball is launched across the floor, but you do not see its entire "
        "trajectory, due to a large occluding wall which descends in front "
        "of you; you must then determine which side of the room contains "
        "the soccer ball, find it, and use PickupObject on it to pick it "
        "up, which completes the scenario. To access a side of the room, "
        "you must open one of the doors (using the OpenObject action) in "
        "the occluding wall. This is a \"forced choice\" task: once you "
        "open the door to one side of the room, you are unable to access "
        "the other side of the room (because it is blocked by lava)."
    )

    # NYU Passive Agency Tasks (in alphabetical order)
    PASSIVE_AGENT_AGENT_NON_AGENT = (
        "Passive Agent: Agent/Non-Agent tasks require a common-sense "
        "understanding of agency. This is a \"passive agents\" task: you "
        "must watch (using only Pass actions) as an ambiguous agent-like "
        "entity (blob shape) moves in a grid world over 8 \"familiarization\""
        " trials and a \"test\" trial (the world \"resets\" between each trial"
        " using the EndHabituation action). The familiarization trials depict "
        "the entity approaching a specific object (the same object in all 8 "
        "familiarization trials). The entity is either an agent or a "
        "non-agent: agents move autonomously, while non-agents are moved "
        "because they are hit by the spinning \"paddle\". You must then "
        "determine whether the test trial is \"more expected\" "
        "(unsurprising) or \"more unexpected\" (surprising) based on how "
        "the entity acts: if the entity is an agent, it should continue to "
        "act with the same preferences it showed during the familiarization "
        "trials (approaching the same object); if the entity is a non-agent, "
        "then it doesn't have preferences, because its movement is controlled"
        " by the paddle, so it's just as likely to approach either object."
    )

    PASSIVE_AGENT_EFFICIENT_ACTION_IRRATIONAL = (
        "Passive Agent: Efficient action (irrational) tasks require a "
        "common-sense understanding of agency. This is a \"passive agents\" "
        "task: you must watch (using only Pass actions) as an agent (blob "
        "shape) moves in a grid world over 8 \"familiarization\" "
        "trials and a \"test\" trial (the world \"resets\" between each trial "
        "using the EndHabituation action). During familiarization, there are "
        "two types of trials: the first shows the agent navigating towards a "
        "goal, taking a longer route even though there may not be obstacles "
        "in the way (hence the agent is inefficient); the second features "
        "the agent moving towards the goal more directly, sometimes having "
        "to maneuver around obstacles (hence, the agent is efficient). "
        "We only show the inefficient action in the test trial. "
        "You must determine whether the test trial is \"expected\" "
        "(unsurprising) or \"unexpected\" (surprising) based on whether or "
        "not the agent exhibits the same level of efficiency shown in the "
        "familiarization trials."
    )

    PASSIVE_AGENT_MULTIPLE_AGENTS = (
        "Passive Agent: Multiple agents tasks require a common-sense "
        "understanding of agency. This is a \"passive agents\" task: you "
        "must watch (using only Pass actions) as an agent (blob shape) "
        "moves in a grid world over 8 \"familiarization\" trials and a "
        "\"test\" trial (the world \"resets\" between each trial using the "
        "EndHabituation action). The familiarization trials feature an "
        "agent repeatedly approaching one of the two objects. You must "
        "then determine whether the test trial is \"more expected\" "
        "(unsurprising) or \"more unexpected\" (surprising) based on how "
        "the agent acts: if the agent is the same agent from familiarization,"
        " it should continue to act with the same preferences it showed in "
        "previous trials (approaching the same object); the "
        "\"more unexpected\" case here would feature a new agent going "
        "to the same object, or the same agent approaching the previously "
        "non-approached object. "
    )

    PASSIVE_AGENT_OBJECT_PREFERENCE = (
        "Passive Agent: Object Preference tasks require a common-sense "
        "understanding of agency. This is a \"passive agents\" task: you must "
        "watch (using only Pass actions) as an agent (blob shape) moves in a "
        "grid world over 8 \"familiarization\" trials and a \"test\" trial "
        "(the world \"resets\" between each trial using the EndHabituation "
        "action). The familiarization trials depict the agent approaching a "
        "specific object (the same object in all 8 familiarization trials). "
        "You must then determine whether the test trial is \"expected\" "
        "(unsurprising) or \"unexpected\" (surprising) based on whether or "
        "not the agent continued to act with the same preferences it showed "
        "during the familiarization trials (approaching the same object)."
    )

    PASSIVE_AGENT_SOCIAL_APPROACH = (
        "Passive Agent: Approach tasks require a common-sense understanding "
        "of agency. This is a \"passive agents\" task: you must watch (using "
        "only Pass actions) as three agents (blob shapes) move in a grid "
        "world over 8 \"familiarization\" trials and a \"test\" trial (the "
        "world \"resets\" between each trial using the EndHabituation action)."
        " The familiarization trials depict an agent approaching another "
        "specific agent (the same agent in all 8 familiarization trials). "
        "You must then determine whether the test trial is \"expected\" "
        "(unsurprising) or \"unexpected\" (surprising) based on whether or "
        "not the agent continued to act with the same preferences it showed "
        "during the familiarization trials (imitating the movement pattern "
        "of the other agent it approached)."
    )

    PASSIVE_AGENT_SOCIAL_IMITATION = (
        "Passive Agent: Imitation tasks require a common-sense understanding "
        "of agency. This is a \"passive agents\" task: you must watch (using "
        "only Pass actions) as three agents (blob shapes) move in a grid "
        "world over 8 \"familiarization\" trials and a \"test\" trial (the "
        "world \"resets\" between each trial using the EndHabituation action)."
        " The familiarization trials depict the three agents moving in "
        "specific patterns, which are consistent across all 8 trials; two "
        "of the agents always have the same movement pattern. You must then"
        " determine whether the test trial is \"expected\" (unsurprising) or "
        "\"unexpected\" (surprising) based on whether or not the agent "
        "continued to act with the same preferences it showed during the "
        "familiarization trials (approaching the other agent who had the "
        "same movement pattern)."
    )

    # Passive Physics Tasks (in alphabetical order)
    PASSIVE_PHYSICS_COLLISION = (
        "Passive Collision tasks require a common-sense understanding of "
        "collision physics. This is a \"passive physics\" task: you must "
        "watch objects moving in a scene (using only Pass actions) and "
        "determine whether the simulation was \"plausible\" (realistic) "
        "or \"implausible\" (unrealistic) based on whether or not objects "
        "properly collide with one another."
    )

    PASSIVE_PHYSICS_GRAVITY_SUPPORT = (
        "Passive Gravity Support tasks require a common-sense understanding"
        " of gravity. This is a \"passive physics\" task: you must watch "
        "objects moving in a scene (using only Pass actions) and determine "
        "whether the simulation was \"plausible\" (realistic) or "
        "\"implausible\" (unrealistic) based on whether or not objects are "
        "properly supported."
    )

    PASSIVE_PHYSICS_OBJECT_PERMANENCE = (
        "Object Permanence tasks require a common-sense understanding of "
        "object permanence. This is a \"passive physics\" task: you must "
        "watch objects moving in a scene (using only Pass actions) and "
        "determine whether the simulation was \"plausible\" (realistic) "
        "or \"implausible\" (unrealistic) based on whether or not objects "
        "spontaneously appear and/or disappear."
    )

    PASSIVE_PHYSICS_SHAPE_CONSTANCY = (
        "Shape Constancy tasks require a common-sense understanding of "
        "shape constancy. This is a \"passive physics\" task: you must "
        "watch objects moving in a scene (using only Pass actions) and "
        "determine whether the simulation was \"plausible\" (realistic) "
        "or \"implausible\" (unrealistic) based on whether or not objects "
        "spontaneously transform into different shapes."
    )

    PASSIVE_PHYSICS_SPATIO_TEMPORAL_CONTINUITY = (
        "Spatio-Temporal Continuity tasks require a common-sense "
        "understanding of spatial and temporal continuity. This is "
        "a \"passive physics\" task: you must watch objects moving a scene "
        "(using only Pass actions) and determine whether the simulation was "
        "\"plausible\" (realistic) or \"implausible\" (unrealistic) based "
        "on whether or not objects spontaneously teleport across the room."
    )

    # Remaining Passive Agency Task
    PASSIVE_SEEING_LEADS_TO_KNOWING = (
        "Seeing Leads to Knowing tasks require a common-sense understanding "
        "of agency. This is a \"passive\" task: you must watch (using only "
        "Pass actions) as a soccer ball is deposited into a container and "
        "an agent approaches a container, and then determine whether the "
        "simulation was \"plausible\" (realistic) or \"implausible\" "
        "(unrealistic) based on whether or not the agent acted with "
        "common-sense reasoning (if the agent saw the ball being deposited, "
        "it should approach the container holding the ball; otherwise it "
        "should approach one of the containers behind it, because one of "
        "those containers holds the ball)."
    )
