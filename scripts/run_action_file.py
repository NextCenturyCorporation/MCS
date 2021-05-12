import machine_common_sense as mcs

from runner_script import SingleFileRunnerScript


action_list_from_file = []


class ActionFileRunnerScript(SingleFileRunnerScript):
    def read_subclass_args(self, parser):
        parser.add_argument(
            'mcs_scene_filename',
            help='Filename of MCS scene to run'
        )
        parser.add_argument(
            'action_filename',
            help='Filename of MCS actions to run'
        )
        args = parser.parse_args()
        return args, [args.mcs_scene_filename]


def action_callback(scene_data, step_metadata, runner_script):
    if not action_list_from_file:
        with open(runner_script.args.action_filename, 'r') as action_file:
            for line in action_file:
                action_list_from_file.append(line.strip())

    if len(action_list_from_file) <= step_metadata.step_number:
        return None, None

    return mcs.Action.input_to_action_and_params(
        action_list_from_file[step_metadata.step_number]
    )


def main():
    ActionFileRunnerScript('Action File', action_callback)


if __name__ == "__main__":
    main()
