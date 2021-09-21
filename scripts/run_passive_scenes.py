from runner_script import MultipleFileRunnerScript


def action_callback(scene_data, step_metadata, runner_script):
    last_step = 60
    if (
        'goal' in scene_data.keys(
        ) and 'last_step' in scene_data['goal'].keys()
    ):
        last_step = scene_data['goal']['last_step']
    if step_metadata.step_number <= last_step:
        action, params = (
            step_metadata.action_list[len(step_metadata.action_list) - 1]
            if len(step_metadata.action_list) else (None, None)
        )
        return action, params
    return None, None


def main():
    MultipleFileRunnerScript('Passive Scenes', action_callback)


if __name__ == "__main__":
    main()
