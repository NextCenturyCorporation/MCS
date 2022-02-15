#
# Test / demo on how to get the action list from a scene file
#
import machine_common_sense as mcs
from machine_common_sense import GoalMetadata


def show_actions_for_scene():
    scene_data, status = mcs.load_scene_json_file("../scenes/charlie_0001_01.json")
    controller = mcs.create_controller(config_file_or_dict='../config_level1.ini')
    output = controller.start_scene(scene_data)
    goal: GoalMetadata = output.goal
    current_actions = goal.retrieve_action_list_at_step(0)
    print(f"{current_actions}")

def simplify_action_list(default_action_list):
    """The action list looks something like:
    [('CloseObject', {}), ('DropObject', {}), ('MoveAhead', {}), ...
    which is not very user-friendly.  For each of them, remove
    the extra quotes"""
    simple_list = []
    if default_action_list is not None and len(default_action_list) > 0:
        for actionPair in default_action_list:
            if isinstance(actionPair, tuple) and len(actionPair) > 0:
                simple_list.append(actionPair[0])
            else:
                simple_list.append(actionPair)
    return simple_list


if __name__ == "__main__":
    # show_actions_for_scene()
    simple_list = simplify_action_list(GoalMetadata.ACTION_LIST)
    print(f"Simple list {simple_list}")