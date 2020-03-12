import sys
from mcs import MCS
from mcs_action import MCS_Action
from mcs_action_keys import MCS_Action_Keys
from mcs_action_api_desc import MCS_Action_API_DESC

if len(sys.argv) < 3:
    print('Usage: python run_mcs_human_input.py <mcs_unity_build_file> <mcs_config_json_file>')
    sys.exit()

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
    print("--------------- Available Commands ---------------")
    for commandListItem in commandList:
        print("*******************")
        print("Command: " + commandListItem.name)
        print("Usage: " + commandListItem.desc)
        print("ShortcutKey: " + commandListItem.key)
        print("*******************")

    print(" ")
    print("Enter 'exit' to exit the program")
    print(" ")
    print("------------------ End Commands ------------------")

# Execute Input Commands until the user exits the system
def input_commands(): 
    print('Enter your command:')
    userInput = input().split(',')

    if(userInput[0] == 'exit'):
        print("Exiting Human Input Mode")
        return

    try:
        # Map shortcut keys to command value
        print(len(userInput[0]))
        if len(userInput[0]) == 1:
            print("Mapping key to command")
            userInput[0] = MCS_Action[MCS_Action_Keys(userInput[0]).name].value

        print('You entered command: ')
        print(*userInput)
        
        # Run commands that have no parameters
        if len(userInput) < 2:
            output = controller.step(userInput[0])
            print('step=' + str(output.step_number))
            return input_commands()
        # Run commands that have parameters, parse params to send to step function
        else:
            # controller.step won't take params as string, need to recreate
            param1key, param1value = userInput[1].split('=')
            param1key = param1key.strip()

            # this could probably be done more easily, open to suggestions
            if len(userInput) > 3:
                param2key, param2value = userInput[2].split('=')
                param2key = param2key.strip()

                if len(userInput) > 4: 
                    param3key, param3value = userInput[3].split('=')
                    param3ey = param3key.strip()

                    param4key, param4value = userInput[4].split('=')
                    param4key = param4key.strip()

                    output = controller.step(userInput[0], param1key=param1value.strip(), param2key=param2value.strip(), param3key=param3value.strip(), param4key=param4value.strip())
                    print('step=' + str(output.step_number))
                    return input_commands()
                else:
                    output = controller.step(userInput[0], param1key=param1value.strip(), param2key=param2value.strip())
                    print('step=' + str(output.step_number))
                    return input_commands()
            else:
                output = controller.step(userInput[0], param1key=param1value.strip())
                print('step=' + str(output.step_number))
                return input_commands()
    except:
        print("You entered an invalid command or a command not yet implemented, please try again.")
        print("You entered: ")
        print(*userInput)
        return input_commands()

# Run scene loaded in the config data
def run_scene(controller, config_data):
    output = controller.start_scene(config_data)

    build_commands()
    print_commands()
    input_commands()

    sys.exit()

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

