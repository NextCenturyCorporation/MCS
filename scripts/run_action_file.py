from runner_script import SingleFileRunnerScript

import machine_common_sense as mcs

action_list_from_file = []


class ActionFileRunnerScript(SingleFileRunnerScript):
    def _append_subclass_args_to_parser(self, parser):
        parser = super()._append_subclass_args_to_parser(parser)
        parser.add_argument(
            'action_filename',
            help='Filename of MCS actions to run'
        )
        return parser


def action_callback(scene_data, step_metadata, runner_script):
    if not action_list_from_file:
        with open(runner_script.args.action_filename, 'r') as action_file:
            for line in action_file:
                action_list_from_file.append(line.strip())

    if len(step_metadata.action_list) == 1:
        return step_metadata.action_list[0]

    if len(action_list_from_file) <= step_metadata.step_number:
        return None, None

    return mcs.Action.input_to_action_and_params(
        action_list_from_file[step_metadata.step_number]
    )


def main():
    ActionFileRunnerScript('Action File', action_callback)


if __name__ == "__main__":
    main()
