import time
import numpy as np

from machine_common_sense.mcs import MCS

actions = ['Pass']
#actions = [
#    'MoveAhead',
#    'MoveBack',
#    'MoveRight',
#    'MoveLeft',
#    'LookUp',
#    'LookDown',
#    'RotateRight',
#    'RotateLeft',
#    'OpenObject',
#    'CloseObject',
#    'PickupObject'
#]


unity_path = '/home/HQ/dwetherby/Downloads/MCS-AI2-THOR-Unity-App-v0.0.6.x86_64'
file_name = '/home/HQ/dwetherby/Downloads/interaction_scenes/retrieval/retrieval_goal-0001.json'

config_data, status = MCS.load_config_json_file(file_name)

controllers = []
controller = MCS.create_controller(unity_path)
#controller.start_scene(config_data)
controllers.append(controller)

num_envs = 1
steps_per_proc = 1000

count = len(actions)
start = time.time()
for _ in range(steps_per_proc):
    int_actions = np.random.randint(count,size=num_envs)
    #[c.step(controller.wrap_step(action=actions[a])) for c, a in zip(controllers,int_actions)]
    [c.step(action='Pass', renderDepthImage=True) for c, a in zip(controllers,int_actions)]
total_time = time.time()-start
print(f"FPS:{steps_per_proc * num_envs / total_time:.2f}")
#[c.stop() for c in controllers]
