import multiprocessing as mp
import ai2thor.controller
import numpy as np
import time
import os

actions = [
    'MoveAhead',
    'MoveBack',
    'MoveRight',
    'MoveLeft',
    'LookUp',
    'LookDown',
    'RotateRight',
    'RotateLeft',
    'OpenObject',
    'CloseObject',
    'PickupObject'
    # 'PutObject'
    # Teleport and TeleportFull but these shouldn't be allowable actions for an agent
]

unity_app_file_path = '/home/HQ/dwetherby/Downloads/MCS-AI2-THOR-Unity-App-v0.0.6.x86_64'
#unity_app_file_path = '/home/HQ/dwetherby/workspace/ai2thor/unity/foo.x86_64'

def worker(steps_per_proc, sync_event, queue, gpu_id=0, actions=actions):

    os.environ['DISPLAY']=f":{gpu_id}"
    controller = ai2thor.controller.Controller(
        width=300,
        height=300,
        #local_executable_path=unity_app_file_path
    )
    controller.start()
    controller.step(dict(action='Initialize', gridSize=0.25))
    print("Worker with pid:", os.getpid(), "is intialized")
    np.random.seed(os.getpid())
    #inform main process that intialization is successful
    queue.put(1)
    sync_event.wait()
    count = len(actions)
    for _ in range(steps_per_proc):
        a = np.random.randint(count)
        controller.step(dict(action=actions[a]))

    queue.put(1)
    print("Worker with pid:", os.getpid(), " funished job")
    sync_event.clear()
    sync_event.wait()
    controller.stop()

def single_worker(num_envs, steps_per_proc, actions=actions):

    controllers=[]
    print(f"num_envs={num_envs}")
    for i in range(num_envs):
        controller = ai2thor.controller.Controller(
            width=300,
            height=300,
            local_executable_path=unity_app_file_path
        )
        controller.start()
        controller.step(dict(action='Initialize', gridSize=0.25))
        controllers.append(controller)

    print(len(controllers))
    count = len(actions)
    start = time.time()
    for _ in range(steps_per_proc):
        int_actions = np.random.randint(count,size=num_envs)
        [c.step(dict(action=actions[a])) for c, a in zip(controllers,int_actions)]
    total_time = time.time()-start
    print(f"FPS:{steps_per_proc *num_envs / total_time:.2f}")
    [c.stop() for c in controllers]


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--multi-processes','-mp', action='store_true', default=False,
                        help="if False, then only one process creates multi envs")
    parser.add_argument('--gpus',type=int,default=1)
    parser.add_argument('--steps', type=int, default=1000)
    parser.add_argument('--num-envs','-n', type=int, default=1)
    args = parser.parse_args()

    if args.multi_processes:
        num_proc = args.num_envs
        steps_per_proc = args.steps//num_proc
        gpuIds = [i%args.gpus for i in range(num_proc)]
        events = [mp.Event() for _ in range(num_proc)]
        [e.clear() for e in events]
        queue = mp.SimpleQueue()
        processes=[]
        for i in range(num_proc):
            p = mp.Process(target=worker, args=(steps_per_proc, events[i], queue, gpuIds[i]))
            p.start()
            processes.append(p)

        initialized_processes = 0
        while(initialized_processes<num_proc):
            queue.get()
            initialized_processes +=1

        start_time= time.time()
        # start test
        [e.set() for e in events]

        finished_processes = 0
        while (finished_processes < num_proc):
            queue.get()
            finished_processes += 1

        total_time = time.time()-start_time

        print(f"FPS:{args.steps/total_time:.2f}")
        # inform process to exit
        [e.set() for e in events]
        for p in processes:
            p.join()
        print("Test finished")

    else:
        print('single worker')
        steps_per_proc = args.steps//args.num_envs
        single_worker(args.num_envs, steps_per_proc)