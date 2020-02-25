import json
import sys
from controller_ai2thor import Controller_AI2THOR

if len(sys.argv) < 3:
    print('Usage: python run_mcs_environment.py <mcs_unity_build_file> <mcs_config_json_file>')
    sys.exit()

def create_controller(unity_app_path):
    # TODO: Toggle between AI2-THOR and other controllers like ThreeDWorld or ML-Agents
    return Controller_AI2THOR(unity_app_path)

# TODO: Add config_name to config_data file (and in Unity class)
def run_scene(controller, config_name, config_data):
    output = controller.reset_scene(config_name, config_data)
    print('step=' + str(output.step_number))

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
        print('step=' + str(output.step_number))

    # Test error case for invalid params for RotateLook (will log a message and then Pass)
    rotateAngle = 400
    output = controller.step('RotateLook', rotation=rotateAngle, horizon=lookAngle)
    print('step=' + str(output.step_number))

if __name__ == "__main__":
    config_data = {}

    with open(sys.argv[2], encoding='utf-8-sig') as config_file:
        config_data = json.load(config_file)

    controller = create_controller(sys.argv[1])
    config_file_path = sys.argv[2]
    config_file_name = config_file_path[config_file_path.rfind('/'):]
    run_scene(controller, config_file_name[0:config_file_name.find('.')], config_data)

