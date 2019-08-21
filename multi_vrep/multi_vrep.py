from wrapper.wrapper_vrep import VREPQuad

print('successfully imported VREP Wrapper Quadrotor!!')

"""
Try tu run multiple instances of vrep safety with multiprocess or threading packages
"""


import numpy as np
from multiprocessing import Process, Pipe


class ParallelVRepExecutor(object):
    """
    Wrap multiples instances of vrep without loss the id connection
    """
    
    def __init__(self, ports, max_path_length):
        """
        Initialize Pipes and Process
        """
        n_parallel  =   len(ports)

        self.remotes, self.work_remotes =   zip(*[Pipe() for _ in range(n_parallel)])
        seeds = np.random.choice(range(10**6), size=n_parallel, replace=False)   
        self.ps = [
            Process(target=self.worker, args=(work_remote, remote, max_path_length, seed, port)) 
            for work_remote, remote, seed, port in zip(self.work_remotes, self.remotes, seeds, ports)
        ]

        for p in self.ps:
            p.daemon = True
            p.start()
        
        for remote in self.work_remotes:
            remote.close()

    def step(self, actions_):
        
        """
        Step for each environment
        """

        for remote, action_list in zip(self.remotes, actions_):
            remote.send(('step', action_list))

        results = [remote.recv() for remote in self.remotes]
        #print(results)
        obs, rws, dones, env_infos = map(lambda x: x, zip(*results))
        #print(obs)
        #print(rws)    
        print(dones)
        #print(env_infos)
        return obs, rws, dones, env_infos
    
    def reset(self):
        """
        Reset all environments
        """
        for remote in self.remotes:
            remote.send(('reset', None))
        
        #print(self.remotes[0].recv())
        #print(self.remotes[1].recv())
        observations = [np.asarray(remote.recv(), np.float32) for remote in self.remotes]
        return observations
    


    def worker(self, remote, parent_remote, max_path_length, seed, port_):
        env = VREPQuad(port=port_)
        np.random.seed(seed)
        max_path_length = max_path_length[0]
        ts = 0
        while True:
            cmd, data = remote.recv()

            if cmd == 'step':
                action  = data
                nextobs, rw, done, info = env.step(action)
                ts = ts + 1
                if done or ts >= max_path_length:
                    done = True
                    env.reset()
                    ts = 0
                """Send the next observation"""
                remote.send((nextobs, rw, done, info))
            elif cmd =='reset':
                """
                Reset the environment associated with the worker
                """
                obs = env.reset()
                remote.send(obs)