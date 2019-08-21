"""
    Command to run vrep
    ./vrep.sh -h -gREMOTEAPISERVERSERVICE_19999_FALSE_TRUE /to/xxxscene.txt
"""
from multi_vrep.multi_vrep import ParallelVRepExecutor
import numpy as np

max_path_length =   250,
ports           =   [19999, 20001]
wrapper         =   ParallelVRepExecutor(ports, max_path_length)

n_parallel      =   len(ports)

for ep in range(100):
    ob      =   wrapper.reset()
    done    =   False
    while not done:
        actions = [np.random.randn(18) for _ in range(n_parallel)]
        obs, rws, dones, infos = wrapper.step(actions)