from runner_script import MultipleFileRunnerScript


def action_callback(scene_data, step_metadata, runner_script):
    return 'Pass', {}


def main():
    MultipleFileRunnerScript('Interactive Scenes - Pass', action_callback)


if __name__ == "__main__":
    main()
