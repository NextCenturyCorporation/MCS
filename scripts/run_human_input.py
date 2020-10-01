import argparse
import cmd

import machine_common_sense as mcs

commandList = []


def parse_args():
    parser = argparse.ArgumentParser(description='Run MCS')
    parser.add_argument(
        'mcs_unity_build_file',
        help='Path to MCS unity build file')
    parser.add_argument(
        'mcs_config_json_file',
        help='MCS JSON scene configuration file to load')
    parser.add_argument(
        '--debug',
        default=False,
        action='store_true',
        help='Generate MCS debug files [default=False]')
    parser.add_argument(
        '--noise',
        default=False,
        action='store_true',
        help='Add random noise to action paramenters ' +
        '(currently only movement/rotation) [default=False]')
    parser.add_argument(
        '--seed',
        type=int,
        default=None,
        help='Python random seed [default=None]')
    parser.add_argument(
        '--size',
        type=int,
        default=None,
        help='Screen width of 450+ (height = width * 2/3) [default=600]')
    parser.add_argument(
        '--depth_masks',
        default=False,
        action='store_true',
        help='Render and return depth masks of each scene ' +
        '(will slightly decrease performance) [default=False]')
    parser.add_argument(
        '--object_masks',
        default=False,
        action='store_true',
        help='Render and return object (instance segmentation) masks of ' +
        'each scene (will significantly decrease performance) [default=False]')
    return parser.parse_args()


class command:
    '''Class to contain possible commands and keys.'''

    def __init__(self, name, key, desc):
        self.name = name
        self.key = key
        self.desc = desc


class HumanInputShell(cmd.Cmd):

    prompt = '(command)->'

    def __init__(
            self,
            input_controller,
            input_previous_output,
            input_config_data):
        super(HumanInputShell, self).__init__()

        self.controller = input_controller
        self.previous_output = input_previous_output
        self.config_data = input_config_data

    def precmd(self, line):
        return line

    def postcmd(self, stopFlag, line) -> bool:
        print('================================================='
              '==============================')
        return stopFlag

    def default(self, line):

        if self.previous_output.action_list is not None and len(
                self.previous_output.action_list) < len(commandList):
            print('Only actions available during this step:')
            for action in self.previous_output.action_list:
                print('  ' + action)
        else:
            print('All actions are available during this step.')

        if self.previous_output.action_list is not None and len(
                self.previous_output.action_list) == 1:
            print('Automatically selecting the only available action...')
            userInput = self.previous_output.action_list[0]
        else:
            userInput = line.split(',')

        # Check for shortcut key, if attempted shortcut key, map and check
        # valid key
        try:
            if len(userInput[0]) == 1:
                userInput[0] = mcs.Action(userInput[0]).value
        except BaseException:
            print(
                "You entered an invalid shortcut key, please try again. "
                "(Type 'help' to display commands again)")
            print("You entered: " + userInput[0])
            return

        if userInput and userInput[0].lower() == 'exit':
            self.do_exit(line)
            return
        if userInput and userInput[0].lower() == 'help':
            self.do_help(line)
            return
        if userInput and userInput[0].lower() == 'reset':
            self.do_reset(line)
            return

        action, params = mcs.Util.input_to_action_and_params(
            ','.join(userInput))

        if action is None:
            print(
                "You entered an invalid command, please try again.  "
                "(Type 'help' to display commands again)")
            return

        if params is None:
            print(
                "ERROR: Parameters should be separated by commas, and "
                "look like this example: rotation=45")
            return

        output = self.controller.step(action, **params)
        self.previous_output = output

    def help_print(self):
        print("Prints all commands that the user can use.")

    def help_exit(self):
        print("Exits out of the MCS Human Input program.")

    def help_reset(self):
        print("Resets the scene.")

    def help_shortcut_key_mode(self):
        print("Toggles on mode where the user can execute single key "
              "commands without hitting enter.")

    def do_exit(self, args) -> bool:
        print("Exiting Human Input Mode\n")
        self.controller.end_scene('plausible')
        return True

    def do_print(self, args):
        print_commands()

    def do_reset(self, args):
        self.previous_output = (self.controller).start_scene(self.config_data)

    def do_shortcut_key_mode(self, args):
        print("Entering shortcut mode...")
        print("Press key 'e' to exit\n")
        list_of_action_keys = [
            action.key for action in mcs.Action]

        while True:
            char = mcs.getch.__call__()
            print('\n(shortcut-command)->', char)
            if char == 'e':  # exit shortcut key mode
                break
            elif char in list_of_action_keys:
                self.default(char)


def build_commands():
    '''Define all the possible human input commands.'''
    for action in mcs.Action:
        commandList.append(command(action.value,
                                   action.key,
                                   action.desc))


def print_commands():
    '''Display all the possible commands and key mappings to the user.'''
    print(" ")
    print("--------------- Available Commands ---------------")
    print(" ")

    for commandListItem in commandList:
        print(
            "- " +
            commandListItem.name +
            " (ShortcutKey=" +
            commandListItem.key +
            "): " +
            commandListItem.desc)

    print(" ")
    print("---------------- Example Commands ----------------")
    print(" ")
    print("MoveAhead")
    print("RotateLook, rotation=45, horizon=15")
    print(" ")
    print("----------------- Other Commands -----------------")
    print(" ")
    print("Enter 'print' to print the commands again.")
    print("Enter 'reset' to reset the scene.")
    print("Enter 'exit' to exit the program.")
    print("Enter 'shortcut_key_mode' to be able to enter Commands "
          "without hitting enter.")
    print(" ")
    print("----------------- Features -----------------------")
    print("Up/Down arrow keys go through the command history")
    print("Tab key is for auto completion of a command")
    print("------------------ End Commands ------------------")
    print(" ")


def run_scene(controller, config_data):
    '''Run scene loaded in the config data.'''
    build_commands()
    print_commands()

    output = controller.start_scene(config_data)

    input_commands = HumanInputShell(controller, output, config_data)
    input_commands.cmdloop()


def main():
    args = parse_args()
    config_data, status = mcs.load_config_json_file(args.mcs_config_json_file)

    if status is not None:
        print(status)
        exit()

    controller = mcs.create_controller(args.mcs_unity_build_file,
                                       debug=args.debug,
                                       enable_noise=args.noise,
                                       seed=args.seed,
                                       size=args.size,
                                       depth_masks=args.depth_masks,
                                       object_masks=args.object_masks)

    config_file_path = args.mcs_config_json_file
    config_file_name = config_file_path[config_file_path.rfind('/') + 1:]

    if 'name' not in config_data.keys():
        config_data['name'] = config_file_name[0:config_file_name.find('.')]

    if controller is not None:
        run_scene(controller, config_data)


if __name__ == "__main__":
    main()
