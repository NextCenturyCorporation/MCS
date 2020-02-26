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

    # Testing RotateLook
    # Rotate and look starting angles
    rotateAngle = -45
    lookAngle = -15
    output = controller.step('RotateLook', rotation=rotateAngle, horizon=lookAngle)
    print('step=' + str(output.step_number))

    # Relative values to continue rotating/looking
    rotateAngle = 10
    lookAngle = 5
    for i in range(1, 6):
        output = controller.step('RotateLook', rotation=rotateAngle, horizon=lookAngle)

    # Test error case for invalid params for RotateLook (will log a message and then Pass)
    lookAngle = 180
    output = controller.step('RotateLook', rotation=rotateAngle, horizon=lookAngle)

if __name__ == "__main__":
    config_data, status = MCS.load_config_json_file(sys.argv[2])

    if status is not None:
        print(status)
        exit()

    controller = MCS.create_controller(sys.argv[1], debug=True)

    config_file_path = sys.argv[2]
    config_file_name = config_file_path[config_file_path.rfind('/'):]

    # TODO: Read name directly from JSON in config file
    config_data['name'] = config_file_name[0:config_file_name.find('.')]

    run_scene(controller, config_data)

