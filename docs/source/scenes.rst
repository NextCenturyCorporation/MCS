Example Scenes
==============

:doc:`Documentation <schema>`

Interactive Scenes
------------------

Playroom
********

An open room containing over 40 objects for undirected exploration.

.. list-table::

    * - .. figure:: /images/playroom_3_2.gif

           :download:`playroom.json <scenes/playroom.json>`

Retrieval Goal
**************

Soccer ball retrieval goal for the Summer 2021 evaluation:

:download:`retrieval_goal_example_with_soccer_ball.json <./scenes/retrieval_goal_example_with_soccer_ball.json>`

Silver trophy retrieval goal for the Winter 2020 evaluation:

:download:`retrieval_goal_example_with_trophy.json <./scenes/retrieval_goal_example_with_trophy.json>`

Hinged Containers
*****************

Soccer ball inside hinged containers for the Summer 2021 evaluation:

.. list-table::

    * - .. figure:: ./images/hinged_container_example_with_soccer_ball.gif

           :download:`hinged_container_example_with_soccer_ball.json <./scenes/hinged_container_example_with_soccer_ball.json>`

Silver trophy inside hinged containers for the Winter 2020 evaluation:

.. list-table::

    * - .. figure:: ./images/hinged_container_example_with_trophy.gif

           :download:`hinged_container_example_with_trophy.json <./scenes/hinged_container_example_with_trophy.json>`

Interactive Object Permanence and Reorientation Tasks
*****************************************************

The room has different dimensions/bounds, and isn't necessarily square. Previously, the room's dimensions were always [-5, 5] on both the X and the Z axes.

.. list-table::

    * - .. figure:: ./images/template_12_by_8.gif

           :download:`template_12_by_8.json <./scenes/template_12_by_8.json>`

    * - .. figure:: ./images/template_2_by_4.gif

           :download:`template_2_by_4.json <./scenes/template_2_by_4.json>`

The room's outer walls are individually, distinctly colored. Previously, all of the room's outer walls were always the same color.

.. list-table::

    * - .. figure:: ./images/template_individually_colored_walls.gif

           :download:`template_individually_colored_walls.json <./scenes/template_individually_colored_walls.json>`

The performer agent is positioned on top of a flat, raised platform. Moving off the edge of the platform will cause the performer agent to automatically, instantaneously fall down to the floor, and the performer agent will not be able to move back on top of the platform.

.. list-table::

    * - .. figure:: ./images/template_platform_independent.gif

           :download:`template_platform_independent.json <./scenes/template_platform_independent.json>`

    * - .. figure:: ./images/template_platform_bisecting.gif

           :download:`template_platform_bisecting.json <./scenes/template_platform_bisecting.json>`

The performer agent is temporarily "frozen" (can only use the Pass action) at the start and/or in the middle of an interactive scene. This is done by the same method that is used for the passive/VoE scenes (see the StepMetadata.action_list property).

.. list-table::

    * - .. figure:: ./images/template_frozen_first_10_steps.gif

           :download:`template_frozen_first_10_steps.json <./scenes/template_frozen_first_10_steps.json>`

    * - .. figure:: ./images/template_frozen_after_10_steps.gif

           :download:`template_frozen_after_10_steps.json <./scenes/template_frozen_after_10_steps.json>`

A cylindrical mechanism attached to a wall or the ceiling throws (for interactive object permanence) or drops (for reorientation) the target object (i.e. soccer ball) into the scene.

.. list-table::

    * - .. figure:: ./images/template_mechanism_dropping_soccer_ball.gif

           :download:`template_mechanism_dropping_soccer_ball.json <./scenes/template_mechanism_dropping_soccer_ball.json>`

    * - .. figure:: ./images/template_mechanism_throwing_soccer_ball.gif

           :download:`template_mechanism_throwing_soccer_ball.json <./scenes/template_mechanism_throwing_soccer_ball.json>`

The performer agent is "kidnapped" (can only call the EndHabituation action) and teleported to another position in the current room one or more times. Prior to being kidnapped, the performer agent is able to move around and explore its environment for a limited number of steps. On the kidnapped step, the returned images will be black. Prior to the final kidnapping, StepMetadata.habituation_trial will be an integer; after the final kidnapping, StepMetadata.habituation_trial will be "None" to denote the test trial.

.. list-table::

    * - .. figure:: ./images/template_kidnapping.gif

           :download:`template_kidnapping.json <./scenes/template_kidnapping.json>`

    * - .. figure:: ./images/template_kidnapping_then_frozen.gif

           :download:`template_kidnapping_then_frozen.json <./scenes/template_kidnapping_then_frozen.json>`

Combination of multiple elements. For example: a platform, being frozen, and a mechanism throwing the soccer ball into the scene.

.. list-table::

    * - .. figure:: ./images/template_interactive_object_permanence_scene.gif

           :download:`template_interactive_object_permanence_scene.json <./scenes/template_interactive_object_permanence_scene.json>`

Intuitive Physics Scenes
------------------------

Gravity Support: Objects Falling Down
*************************************

All of these examples are PLAUSIBLE

.. list-table::

    * - .. figure:: ./images/gravity_support_ex_01.gif

           :download:`gravity_support_ex_01.json <./scenes/gravity_support_ex_01.json>`

    * - .. figure:: ./images/gravity_support_ex_02.gif

           :download:`gravity_support_ex_02.json <./scenes/gravity_support_ex_02.json>`

    * - .. figure:: ./images/gravity_support_ex_03.gif

           :download:`gravity_support_ex_03.json <./scenes/gravity_support_ex_03.json>`

    * - .. figure:: ./images/gravity_support_ex_04.gif

           :download:`gravity_support_ex_04.json <./scenes/gravity_support_ex_04.json>`

    * - .. figure:: ./images/gravity_support_ex_05.gif

           :download:`gravity_support_ex_05.json <./scenes/gravity_support_ex_05.json>`

    * - .. figure:: ./images/gravity_support_ex_06.gif

           :download:`gravity_support_ex_06.json <./scenes/gravity_support_ex_06.json>`

    * - .. figure:: ./images/gravity_support_ex_07.gif

           :download:`gravity_support_ex_07.json <./scenes/gravity_support_ex_07.json>`

    * - .. figure:: ./images/gravity_support_ex_08.gif

           :download:`gravity_support_ex_08.json <./scenes/gravity_support_ex_08.json>`

    * - .. figure:: ./images/gravity_support_ex_09.gif

           :download:`gravity_support_ex_09.json <./scenes/gravity_support_ex_09.json>`

    * - .. figure:: ./images/gravity_support_ex_10.gif

           :download:`gravity_support_ex_10.json <./scenes/gravity_support_ex_10.json>`

    * - .. figure:: ./images/gravity_support_ex_11.gif

           :download:`gravity_support_ex_11.json <./scenes/gravity_support_ex_11.json>`

    * - .. figure:: ./images/gravity_support_ex_12.gif

           :download:`gravity_support_ex_12.json <./scenes/gravity_support_ex_12.json>`


Object Permanence and Spatio-Temporal Continuity: Objects Moving on Multiple Axes Behind Occluders
**************************************************************************************************

Relevant for the Summer 2021 evaluation. Objects may move on only the X axis (as in previous evaluations), on both the X and Z axes (see the "move deep" example scenes), and/or on both the X and Y axes (see the "move toss" example scenes).

.. list-table::

    * - .. figure:: ./images/move_deep_fast_01.gif

           :download:`move_deep_fast_01.json <./scenes/move_deep_fast_01.json>`

    * - .. figure:: ./images/move_deep_fast_02.gif

           :download:`move_deep_fast_02.json <./scenes/move_deep_fast_02.json>`

    * - .. figure:: ./images/move_deep_fast_03.gif

           :download:`move_deep_fast_03.json <./scenes/move_deep_fast_03.json>`

    * - .. figure:: ./images/move_deep_fast_04.gif

           :download:`move_deep_fast_04.json <./scenes/move_deep_fast_04.json>`

    * - .. figure:: ./images/move_toss_fast_01.gif

           :download:`move_toss_fast_01.json <./scenes/move_toss_fast_01.json>`

    * - .. figure:: ./images/move_toss_fast_02.gif

           :download:`move_toss_fast_02.json <./scenes/move_toss_fast_02.json>`

Object Permanence: Objects Moving on Multiple Axes and Stopping Behind Occluders
********************************************************************************

Relevant for the Summer 2021 evaluation. Objects may move across the entire screen and exit on the other side (as in previous evaluations), or come to a natural stop behind the occluder. Objects may move on only the X axis (as in previous evaluations), on both the X and Z axes (see the "move deep" example scenes), and/or on both the X and Y axes (see the "move toss" example scenes).

.. list-table::

    * - .. figure:: ./images/move_slow_01.gif

           :download:`move_slow_01.json <./scenes/move_slow_01.json>`
    
    * - .. figure:: ./images/move_slow_02.gif

           :download:`move_deep_slow_01.json <./scenes/move_deep_slow_01.json>`

    * - .. figure:: ./images/move_deep_slow_01.gif

           :download:`move_toss_slow_01.json <./scenes/move_toss_slow_01.json>`

    * - .. figure:: ./images/move_deep_slow_02.gif

           :download:`move_slow_02.json <./scenes/move_slow_02.json>`

    * - .. figure:: ./images/move_toss_slow_01.gif

           :download:`move_deep_slow_02.json <./scenes/move_deep_slow_02.json>`

    * - .. figure:: ./images/move_toss_slow_02.gif

           :download:`move_toss_slow_02.json <./scenes/move_toss_slow_02.json>`


Object Permanence: Objects Falling Down Behind Occluders
********************************************************

Relevant for the Winter 2020 evaluation.

.. list-table::

    * - .. figure:: ./images/object_permanence_plausible.gif

           :download:`object_permanence_plausible.json <./scenes/object_permanence_plausible.json>`

    * - .. figure:: ./images/object_permanence_implausible.gif

           :download:`object_permanence_implausible.json <./scenes/object_permanence_implausible.json>`

Spatio-Temporal Continuity: Objects Moving Across Behind Occluders
******************************************************************

Relevant for the Winter 2020 evaluation.

.. list-table::

    * - .. figure:: ./images/spatio_temporal_continuity_plausible.gif

           :download:`spatio_temporal_continuity_plausible.json <./scenes/spatio_temporal_continuity_plausible.json>`

    * - .. figure:: ./images/spatio_temporal_continuity_implausible.gif

           :download:`spatio_temporal_continuity_implausible.json <./scenes/spatio_temporal_continuity_implausible.json>`

Agents Scenes
-------------

Agents Have Goals and Preferences
*********************************

.. list-table::

    * - .. figure:: ./images/agents_preference_expected.gif

           :download:`agents_preference_expected.json <./scenes/agents_preference_expected.json>`

    * - .. figure:: ./images/agents_preference_unexpected.gif

           :download:`agents_preference_unexpected.json <./scenes/agents_preference_unexpected.json>`


Simple Scenes
-------------

With Objects
************

:download:`ball_close.json <./scenes/ball_close.json>`

:download:`ball_far.json <./scenes/ball_far.json>`

:download:`ball_obstructed.json <./scenes/ball_obstructed.json>`

:download:`block_close.json <./scenes/block_close.json>`


With Walls
**********

:download:`wall_ahead.json <./scenes/wall_ahead.json>`

:download:`wall_diagonal.json <./scenes/wall_diagonal.json>`

:download:`wall_offset.json <./scenes/wall_offset.json>`

:download:`wall_right.json <./scenes/wall_right.json>`
