from .runner_script import SingleFileRunnerScript


def action_callback(scene_data, step_metadata, runner_script):
    last_step = 60
    if (
        'goal' in scene_data.keys(
        ) and 'last_step' in scene_data['goal'].keys()
    ):
        last_step = scene_data['goal']['last_step']
    if step_metadata.step_number < last_step:
        return 'Pass', {}
    return None, None


def main():
    SingleFileRunnerScript('Just Pass', action_callback)


if __name__ == "__main__":
    main()
