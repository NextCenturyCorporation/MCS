import argparse
import cmd

import machine_common_sense as mcs
from machine_common_sense.goal_metadata import GoalMetadata
from machine_common_sense.logging_config import LoggingConfig

from .getch_helper import getch

commandList = []


def parse_args():
    parser = argparse.ArgumentParser(description='Run MCS')
    parser.add_argument(
        'mcs_scene_json_file',
        help='MCS JSON scene configuration file to load')
    parser.add_argument(
        '--mcs_unity_build_file',
        type=str,
        default=None,
        help='Path to MCS unity build file')
    parser.add_argument(
        '--mcs_unity_version',
        type=str,
        default=None,
        help='version of MCS Unity executable.  Default: current')
    parser.add_argument(
        '--config_file_path',
        type=str,
        default=None,
        required=True,
        help='Path to configuration file to read in and set various ' +
        'properties, such as metadata level and whether or not to ' +
        'save history files properties.')
    return parser.parse_args()


class command:
    '''Class to contain possible commands and keys.'''

    def __init__(self, name, key, desc):
        self.name = name
        self.key = key
        self.desc = desc


class HumanInputShell(cmd.Cmd):

    prompt = '(command)->'

    def __init__(self, input_controller, input_scene_data):
        super(HumanInputShell, self).__init__()

        self.controller = input_controller
        self.scene_data = input_scene_data
        self.previous_output = None
        self.auto = False

    def precmd(self, line):
        return line

    def postcmd(self, stopFlag, line) -> bool:
        print('================================================='
              '==============================')
        return stopFlag

    def default(self, line):
        split_input = line.split(',')

        # Check for shortcut key, if attempted shortcut key, map and check
        # valid key
        try:
            if len(split_input[0]) == 1:
                split_input[0] = mcs.Action(split_input[0]).value
        except BaseException:
            print(
                "You entered an invalid shortcut key, please try again. "
                "(Type 'help' to display commands again)")
            print("You entered: " + split_input[0])
            return

        if (
            self.auto and self.previous_output.action_list and
            len(self.previous_output.action_list) == 1
        ):
            print('Automatically selecting the only available action...')
            action, params = self.previous_output.action_list[0]
        else:
            action, params = mcs.Action.input_to_action_and_params(
                ','.join(split_input),
            )

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

        # The output may be None if given an invalid action.
        if output:
            self.previous_output = output
            self.show_available_actions(self.previous_output)
            # If auto mode is True, loop as long as possible.
            if (
                self.auto and self.previous_output.action_list and
                len(self.previous_output.action_list) == 1
            ):
                self.default('')

    def help_auto(self):
        print(
            "Automatically runs the next action if only one action is "
            "available at that step.",
        )

    def help_print(self):
        print("Prints all commands that the user can use.")

    def help_exit(self):
        print("Exits out of the MCS Human Input program.")

    def help_reset(self):
        print("Resets the scene.")

    def help_shortcut_key_mode(self):
        print("Toggles on mode where the user can execute single key "
              "commands without hitting enter.")

    def do_auto(self, args=None):
        self.auto = (not self.auto)
        print(f"Toggle auto mode {('ON' if self.auto else 'OFF')}")
        if (
            self.auto and self.previous_output.action_list and
            len(self.previous_output.action_list) == 1
        ):
            self.default('')

    def do_exit(self, args=None) -> bool:
        print("Exiting Human Input Mode\n")
        self.controller.end_scene("", 1)
        return True

    def do_print(self, args=None):
        print_commands()

    def do_reset(self, args=None):
        print("Resetting the current scene...")
        self.previous_output = (self.controller).start_scene(self.scene_data)
        self.show_available_actions(self.previous_output)

    def do_shortcut_key_mode(self, args=None):
        print("Entering shortcut mode...")
        print("Press key 'e' to exit\n")
        list_of_action_keys = [
            action.key for action in mcs.Action]

        while True:
            char = getch.__call__()
            print('\n(shortcut-command)->', char)
            if char == 'e':  # exit shortcut key mode
                break
            elif char in list_of_action_keys:
                self.default(char)

    def show_available_actions(self, output):
        if (
            output.action_list and
            len(output.action_list) < len(GoalMetadata.ACTION_LIST)
        ):
            print('Only actions available during this step:')
            for action, params in output.action_list:
                action_string = action + ''.join(
                    ',' + key + '=' + value for key, value in params.items()
                )

                print(f'    {action_string}')
        else:
            print('All actions available during this step.')


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
    print("RotateLeft")
    print("LookUp")
    print(" ")
    print("----------------- Other Commands -----------------")
    print(" ")
    print("Enter 'auto' to start auto mode.")
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


def run_scene(controller, scene_data):
    '''Run scene loaded in the scene config data.'''
    build_commands()
    print_commands()

    input_commands = HumanInputShell(controller, scene_data)
    input_commands.do_reset()
    input_commands.cmdloop()


def main():
    mcs.init_logging(LoggingConfig.get_dev_logging_config())
    args = parse_args()
    scene_data, status = mcs.load_scene_json_file(args.mcs_scene_json_file)

    if status is not None:
        print(status)
        exit()

    controller = mcs.create_controller(
        unity_app_file_path=args.mcs_unity_build_file,
        config_file_or_dict=args.config_file_path,
        unity_cache_version=args.mcs_unity_version)

    scene_file_path = args.mcs_scene_json_file
    scene_file_name = scene_file_path[scene_file_path.rfind('/') + 1:]

    if 'name' not in scene_data.keys():
        scene_data['name'] = scene_file_name[:scene_file_name.find('.')]

    if controller is not None:
        run_scene(controller, scene_data)


if __name__ == "__main__":
    main()
