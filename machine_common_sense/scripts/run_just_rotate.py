import argparse

from runner_script import SingleFileRunnerScript


def action_callback(scene_data, step_metadata, runner_script):
    if runner_script.args.slow:
        if step_metadata.step_number < 360:
            if step_metadata.step_number % 10 == 0:
                return 'RotateRight', {}
            else:
                return 'Pass', {}
    else:
        if step_metadata.step_number < 36:
            return 'RotateRight', {}
    return None, None


class RotateRunnerScript(SingleFileRunnerScript):
    def _append_subclass_args_to_parser(
        self,
        parser: argparse.ArgumentParser
    ) -> argparse.ArgumentParser:
        parser = super()._append_subclass_args_to_parser(parser)
        parser.add_argument(
            '--slow',
            default=False,
            action='store_true',
            help='Rotate every 10 steps'
        )
        return parser


def main():
    RotateRunnerScript('Just Rotate', action_callback)


if __name__ == "__main__":
    main()
