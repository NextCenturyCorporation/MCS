from run_last_action import action_callback
from runner_script import MultipleFileRunnerScript


def main():
    MultipleFileRunnerScript(
        'Interactive Scenes - Last Action or Rotate',
        action_callback
    )


if __name__ == "__main__":
    main()
