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

    # Testing PutObject (using playroom scene):
    # Move towards apple to pick it up
    output = controller.step('MoveLeft')
    for i in range(1, 4):
        output = controller.step('MoveAhead')

    output = controller.step('RotateLook', rotation=0, horizon=45)

    # Should return SUCCESSFUL
    output = controller.step('PickupObject', objectId="apple_a")

    output = controller.step('MoveLeft')

    # Should return NOT_RECEPTACLE
    output = controller.step('MoveAhead')
    output = controller.step('PutObject', objectId="apple_a", receptacleObjectId="apple_b")

    for i in range(1, 5):
        output = controller.step('MoveAhead')

    # Should return OUT_OF_REACH
    output = controller.step('PutObject', objectId="apple_a", receptacleObjectId="plate_a")

    output = controller.step('MoveAhead')

    # Should return NOT_HELD
    output = controller.step('PutObject', objectId="apple_b", receptacleObjectId="box_a")

    # Should return NOT_OBJECT
    output = controller.step('PutObject', objectId="invalid_apple_a", receptacleObjectId="box_a")
    output = controller.step('PutObject', objectId="apple_a", receptacleObjectId="invalid_box_a")
    
    # Should return SUCCESSFUL
    output = controller.step('PutObject', objectId="apple_a", receptacleObjectId="plate_a")
    
    # Pick up plate and move towards the closed box
    output = controller.step('PickupObject', objectId="plate_a")

    output = controller.step('RotateLook', rotation=160, horizon=-30)
    
    for i in range(1, 8):
        output = controller.step('MoveAhead')

    output = controller.step('RotateLook', rotation=-10, horizon=0)

    for i in range(1, 3):
        output = controller.step('MoveAhead')

    # Should return OBSTRUCTED
    output = controller.step('PutObject', objectId="plate_a", receptacleObjectId="box_b")

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

