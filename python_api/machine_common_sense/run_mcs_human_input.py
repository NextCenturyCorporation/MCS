import sys

from machine_common_sense.mcs import MCS
from machine_common_sense.mcs_action import MCS_Action
from machine_common_sense.mcs_action_api_desc import MCS_Action_API_DESC
from machine_common_sense.mcs_action_keys import MCS_Action_Keys
from machine_common_sense.mcs_util import MCS_Util

# variables
commandList = []

# class to contain possible commands and keys
class command:
    def __init__(self, name, key, desc):
        self.name = name
        self.key = key
        self.desc = desc

# Define all the possible human input commands
def build_commands():
    for action in MCS_Action:
        commandList.append(command(action.value, MCS_Action_Keys[action.name].value, MCS_Action_API_DESC[action.name].value))

# Display all the possible commands to the user along with key mappings
def print_commands():
    print(" ")
    print("--------------- Available Commands ---------------")
    print(" ")

    for commandListItem in commandList:
        print("- " + commandListItem.name + " (ShortcutKey=" + commandListItem.key + "): " + commandListItem.desc)

    print(" ")
    print("---------------- Example Commands ----------------")
    print(" ")
    print("MoveAhead")
    print("RotateLook, rotation=45, horizon=15")
    print(" ")
    print("----------------- Other Commands -----------------")
    print(" ")
    print("Enter 'help' to print the commands again.")
    print("Enter 'exit' to exit the program.")
    print(" ")
    print("------------------ End Commands ------------------")
    print(" ")

# Execute Input Commands until the user exits the system
def input_commands(controller, previous_output):
    if previous_output.action_list is not None and len(previous_output.action_list) < len(commandList):
        print('Only actions available during this step:')
        for action in previous_output.action_list:
            print('  ' + action)
    else:
        print('All actions available during this step.')

    if previous_output.action_list is not None and len(previous_output.action_list) == 1:
        print('Automatically selecting the only available action...')
        userInput = previous_output.action_list[1]
    else:
        print('Enter your command:')
        userInput = input().split(',')

    if(userInput[0].lower() == 'exit'):
        print("Exiting Human Input Mode")
        return

    if(userInput[0].lower() == 'help'):
        print_commands()
        return input_commands(controller, previous_output)

    # Check for shortcut key, if attempted shortcut key, map and check valid key
    try:
        if len(userInput[0]) == 1:
            userInput[0] = MCS_Action[MCS_Action_Keys(userInput[0] ).name].value
    except:
        print("You entered an invalid shortcut key, please try again. (Type 'help' to display commands again)")
        print("You entered: " + userInput[0])
        return input_commands(controller, previous_output)

    print('You entered command:')
    print(*userInput)

    action, params = MCS_Util.input_to_action_and_params(','.join(userInput))

    if action is None:
        print("You entered an invalid command, please try again.  (Type 'help' to display commands again)")
        return input_commands(controller, previous_output)

    if params is None:
        print("ERROR: Parameters should be separated by commas, and look like this example: rotation=45")
        return input_commands(controller, previous_output)

    output = controller.step(action, **params);

    print('===============================================================================')

    return input_commands(controller, output)

# Run scene loaded in the config data
def run_scene(controller, config_data):
    build_commands()
    print_commands()

    output = controller.start_scene(config_data)

    input_commands(controller, output)

    sys.exit()

def main():
    if len(sys.argv) < 3:
        print('Usage: python run_mcs_human_input.py <mcs_unity_build_file> <mcs_config_json_file> <debug_files> <enable_noise>')
        sys.exit()

    config_data, status = MCS.load_config_json_file(sys.argv[2])

    if status is not None:
        print(status)
        exit()

    debug = True
    if sys.argv[3] is not None:
        debug = sys.argv[3].lower() == 'true'

    enable_noise = False
    if sys.argv[4] is not None:
        enable_noise = sys.argv[4].lower() == 'true'

    controller = MCS.create_controller(sys.argv[1], debug=debug, enable_noise=enable_noise)

    config_file_path = sys.argv[2]
    config_file_name = config_file_path[config_file_path.rfind('/'):]

    if 'name' not in config_data.keys():
        config_data['name'] = config_file_name[0:config_file_name.find('.')]

    run_scene(controller, config_data)

if __name__ == "__main__":
    main()

