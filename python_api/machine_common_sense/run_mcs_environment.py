import sys
from machine_common_sense.mcs import MCS

if len(sys.argv) < 3:
    print('Usage: python run_mcs_environment.py <mcs_unity_build_file> '
          '<mcs_config_json_file>')
    sys.exit()


def run_scene(controller, config_data):
    output = controller.start_scene(config_data)

    # Default test code for a scene
    # for i in range(1, 31):
    #    output = controller.step('Pass')
    #    print('step=' + str(output.step_number))

    # Test ThrowObject
    output = controller.step('MoveAhead')
    output = controller.step('MoveAhead')
    output = controller.step('RotateLook', rotation=270, horizon=40)
    output = controller.step('PickupObject', objectId="apple_a")
    output = controller.step('Pass')
    output = controller.step('RotateLook', rotation=0, horizon=-30)
    output = controller.step(
        'ThrowObject',
        objectId="apple_a",
        force=1,
        objectDirectionX=1,
        objectDirectionY=0,
        objectDirectionZ=2)
    output = controller.step('RotateLook', rotation=20, horizon=0)
    output = controller.step('Pass')
    output = controller.step('Pass')
    output = controller.step('Pass')  # noqa: F841


if __name__ == "__main__":
    config_data, status = MCS.load_config_json_file(sys.argv[2])

    if status is not None:
        print(status)
        exit()

    debug = 'terminal' if sys.argv[3] is None else True
    enable_noise = 'terminal' if sys.argv[4] is None else False

    controller = MCS.create_controller(
        sys.argv[1], debug=debug, enable_noise=enable_noise)

    config_file_path = sys.argv[2]
    config_file_name = config_file_path[config_file_path.rfind('/') + 1:]

    # TODO: Read name directly from JSON in config file
    config_data['name'] = config_file_name[0:config_file_name.find('.')]

    run_scene(controller, config_data)
