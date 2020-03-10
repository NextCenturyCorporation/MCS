import sys
from mcs import MCS

if len(sys.argv) < 3:
    print('Usage: python run_mcs_environment.py <mcs_unity_build_file> <mcs_config_json_file>')
    sys.exit()

def run_scene(controller, config_data):
    output = controller.start_scene(config_data)

    # Default test code for a scene
    # for i in range(1, 31):
    #    output = controller.step('Pass')
    #    print('step=' + str(output.step_number))

    # Testing PickupObject and DropObject (using playroom scene):
    # Should return NOT_OBJECT
    output = controller.step('PickupObject', objectId="invalid_object")

    # Move towards apple to pick it up
    for i in range(1, 7):
        output = controller.step('MoveAhead')

    output = controller.step('RotateLook', rotation=0, horizon=35)

    # Should return OUT_OF_REACH
    output = controller.step('PickupObject', objectId="test_ball_1")

    # Should return SUCCESSFUL
    output = controller.step('PickupObject', objectId="test_apple_1")

    # Should return NOT_OBJECT
    output = controller.step('DropObject', objectId="invalid_object")

    # Should return NOT_HELD
    output = controller.step('DropObject', objectId="test_ball_1")

    # Should return SUCCESSFUL
    output = controller.step('DropObject', objectId="test_apple_1")

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

