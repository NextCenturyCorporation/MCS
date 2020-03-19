import sys
from machine_common_sense.mcs import MCS

if len(sys.argv) < 3:
    print('Usage: python run_mcs_environment.py <mcs_unity_build_file> <mcs_config_json_file>')
    sys.exit()

def run_scene(controller, config_data):
    output = controller.start_scene(config_data)

    # Default test code for a scene
    # for i in range(1, 31):
    #    output = controller.step('Pass')
    #    print('step=' + str(output.step_number))

    # Testing PushObject, PullObject (using playroom scene):
    # Move towards apple to pick it up
    output = controller.step('MoveLeft')
    output = controller.step('MoveAhead')

    # Should return OUT_OF_REACH
    output = controller.step('PullObject', objectId="apple_a", force=1)

    output = controller.step('RotateLook', rotation=0, horizon=45)

    # Should return SUCCESSFUL
    output = controller.step('PullObject', objectId="apple_a", force=1)
    output = controller.step('PushObject', objectId="apple_a", force=1)

if __name__ == "__main__":
    config_data, status = MCS.load_config_json_file(sys.argv[2])

    if status is not None:
        print(status)
        exit()

    controller = MCS.create_controller(sys.argv[1], debug=True)

    config_file_path = sys.argv[2]
    config_file_name = config_file_path[config_file_path.rfind('/')+1:]

    # TODO: Read name directly from JSON in config file
    config_data['name'] = config_file_name[0:config_file_name.find('.')]

    run_scene(controller, config_data)

