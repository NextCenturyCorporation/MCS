# MCS Scene Configuration Files: README

## Documentation

[SCHEMA.md](./SCHEMA.md)

## Examples

### Interactive Scenes

#### Playroom

An open room containing over 40 objects for undirected exploration.

- [playroom.json](./playroom.json)

![playroom_3_2](./videos/playroom_3_2.gif)

#### Retrieval Goal

Soccer ball retrieval goal for the Summer 2021 evaluation:

- [retrieval_goal_example_with_soccer_ball.json](./retrieval_goal_example_with_soccer_ball.json)

Silver trophy retrieval goal for the Winter 2020 evaluation:

- [retrieval_goal_example_with_trophy.json](./retrieval_goal_example_with_trophy.json)

#### Hinged Containers

Soccer ball inside hinged containers for the Summer 2021 evaluation:

- [hinged_container_example_with_soccer_ball.json](./hinged_container_example_with_soccer_ball.json)

![hinged_container_example_with_soccer_ball](./videos/hinged_container_example_with_soccer_ball.gif)

Silver trophy inside hinged containers for the Winter 2020 evaluation:

- [hinged_container_example_with_trophy.json](./hinged_container_example_with_trophy.json)

![hinged_container_example_with_trophy](./videos/hinged_container_example_with_trophy.gif)

#### Interactive Object Permanence

Performer agent starts on top of a raised platform and can move off the platform onto the floor but cannot move back onto the platform from the floor.

- [template_platform_singleton.json](./template_platform_singleton.json)
- [template_platform_bisecting.json](./template_platform_bisecting.json)

Performer agent is frozen (can only use the Pass action) during specific steps in the scene.

- [template_frozen_first_10_steps.json](./template_frozen_first_10_steps.json)
- [template_frozen_after_10_steps.json](./template_frozen_after_10_steps.json)

Soccer ball is thrown into the scene via a cylindrical mechanism attached to the ceiling.

- [template_soccer_ball_throwing_mechanism.json](./template_soccer_ball_throwing_mechanism.json)

Combination of the platform, being frozen, and soccer ball being thrown into the scene.

- [template_interactive_object_permanence_scene.json](./template_interactive_object_permanence_scene.json)

#### Reorientation

Rectangular rooms.

- [template_12_by_8.json](./template_12_by_8.json)
- [template_2_by_4.json](./template_2_by_4.json)

Rooms with individually colored outer walls.

- [template_individually_colored_walls.json](./template_individually_colored_walls.json)

Performer agent is frozen (can only use the Pass action) during specific steps in the scene.

- [template_frozen_first_10_steps.json](./template_frozen_first_10_steps.json)
- [template_frozen_after_10_steps.json](./template_frozen_after_10_steps.json)

Soccer ball is dropped into an open container via a cylindrical mechanism attached to the ceiling.

- [template_soccer_ball_dropping_mechanism.json](./template_soccer_ball_dropping_mechanism.json)

Performer agent is kidnapped (can only use the EndHabituation action, which blacks its vision and teleports it to a new location) one or more times.

- [template_kidnapping.json](./template_kidnapping.json)
- [template_kidnapping_then_frozen.json](./template_kidnapping_then_frozen.json)

### Intuitive Physics Scenes

#### Gravity Support: Objects Falling Down

- [gravity_support_ex_01.json](./gravity_support_ex_01.json)
- [gravity_support_ex_02.json](./gravity_support_ex_02.json)
- [gravity_support_ex_03.json](./gravity_support_ex_03.json)
- [gravity_support_ex_04.json](./gravity_support_ex_04.json)
- [gravity_support_ex_05.json](./gravity_support_ex_05.json)
- [gravity_support_ex_06.json](./gravity_support_ex_06.json)
- [gravity_support_ex_07.json](./gravity_support_ex_07.json)
- [gravity_support_ex_08.json](./gravity_support_ex_08.json)
- [gravity_support_ex_09.json](./gravity_support_ex_09.json)
- [gravity_support_ex_10.json](./gravity_support_ex_10.json)
- [gravity_support_ex_11.json](./gravity_support_ex_11.json)
- [gravity_support_ex_12.json](./gravity_support_ex_12.json)

| Plausible |
| --------- |
| ![](./videos/gravity_support_ex_01.gif) | |
| ![](./videos/gravity_support_ex_02.gif) | |
| ![](./videos/gravity_support_ex_03.gif) | |
| ![](./videos/gravity_support_ex_04.gif) | |
| ![](./videos/gravity_support_ex_05.gif) | |
| ![](./videos/gravity_support_ex_06.gif) | |
| ![](./videos/gravity_support_ex_07.gif) | |
| ![](./videos/gravity_support_ex_08.gif) | |
| ![](./videos/gravity_support_ex_09.gif) | |
| ![](./videos/gravity_support_ex_10.gif) | |
| ![](./videos/gravity_support_ex_11.gif) | |
| ![](./videos/gravity_support_ex_12.gif) | |

#### Object Permanence and Spatio-Temporal Continuity: Objects Moving on Multiple Axes Behind Occluders

Relevant for the Summer 2021 evaluation. Objects may move on only the X axis (as in previous evaluations), on both the X and Z axes (see the "move deep" example scenes), and/or on both the X and Y axes (see the "move toss" example scenes).

- [move_deep_fast_01.json](./move_deep_fast_01.json)
- [move_deep_fast_02.json](./move_deep_fast_02.json)
- [move_deep_fast_03.json](./move_deep_fast_03.json)
- [move_deep_fast_04.json](./move_deep_fast_04.json)
- [move_toss_fast_01.json](./move_toss_fast_01.json)
- [move_toss_fast_02.json](./move_toss_fast_02.json)

| | |
| --------- | ----------- |
| ![](./videos/move_deep_fast_01.gif) | ![](./videos/move_deep_fast_02.gif) |
| ![](./videos/move_deep_fast_03.gif) | ![](./videos/move_deep_fast_04.gif) |
| ![](./videos/move_toss_fast_01.gif) | ![](./videos/move_toss_fast_02.gif) |

#### Object Permanence: Objects Moving on Multiple Axes and Stopping Behind Occluders

Relevant for the Summer 2021 evaluation. Objects may move across the entire screen and exit on the other side (as in previous evaluations), or come to a natural stop behind the occluder. Objects may move on only the X axis (as in previous evaluations), on both the X and Z axes (see the "move deep" example scenes), and/or on both the X and Y axes (see the "move toss" example scenes).

- [move_slow_01.json](./move_slow_01.json)
- [move_deep_slow_01.json](./move_deep_slow_01.json)
- [move_toss_slow_01.json](./move_toss_slow_01.json)
- [move_slow_02.json](./move_slow_02.json)
- [move_deep_slow_02.json](./move_deep_slow_02.json)
- [move_toss_slow_02.json](./move_toss_slow_02.json)

| Example 1 | Example 2 |
| --------- | ----------- |
| ![](./videos/move_slow_01.gif) | ![](./videos/move_slow_02.gif) |
| ![](./videos/move_deep_slow_01.gif) | ![](./videos/move_deep_slow_02.gif) |
| ![](./videos/move_toss_slow_01.gif) | ![](./videos/move_toss_slow_02.gif) |

#### Object Permanence: Objects Falling Down Behind Occluders

Relevant for the Winter 2020 evaluation.

- [object_permanence_plausible.json](./object_permanence_plausible.json)
- [object_permanence_implausible.json](./object_permanence_implausible.json)

| Plausible | Implausible |
| --------- | ----------- |
| ![](./videos/object_permanence_plausible.gif) | ![](./videos/object_permanence_implausible.gif) |

#### Shape Constancy: Objects Falling Down Behind Occluders

Relevant for the Winter 2020 and Summer 2021 evaluations

- [shape_constancy_plausible.json](./shape_constancy_plausible.json)
- [shape_constancy_implausible.json](./shape_constancy_implausible.json)

| Plausible | Implausible |
| --------- | ----------- |
| ![](./videos/shape_constancy_plausible.gif) | ![](./videos/shape_constancy_implausible.gif) |

#### Spatio-Temporal Continuity: Objects Moving Across Behind Occluders

Relevant for the Winter 2020 evaluation.

- [spatio_temporal_continuity_plausible.json](./spatio_temporal_continuity_plausible.json)
- [spatio_temporal_continuity_implausible.json](./spatio_temporal_continuity_implausible.json)

| Plausible | Implausible |
| --------- | ----------- |
| ![](./videos/spatio_temporal_continuity_plausible.gif) | ![](./videos/spatio_temporal_continuity_implausible.gif) |

### Agents Scenes

#### Agents Have Goals and Preferences

- [agents_preference_expected.json](./agents_preference_expected.json)
- [agents_preference_unexpected.json](./agents_preference_unexpected.json)

| Plausible | Implausible |
| --------- | ----------- |
| ![](./videos/agents_preference_expected.gif) | ![](./videos/agents_preference_unexpected.gif) |

### Simple Scenes

#### With Objects

- [ball_close.json](./ball_close.json)
- [ball_far.json](./ball_far.json)
- [ball_obstructed.json](./ball_obstructed.json)
- [block_close.json](./block_close.json)

#### With Walls

- [wall_ahead.json](./wall_ahead.json)
- [wall_diagonal.json](./wall_diagonal.json)
- [wall_offset.json](./wall_offset.json)
- [wall_right.json](./wall_right.json)

