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


if __name__ == "__main__":
    show_actions_for_scene()
