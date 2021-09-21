from time import time, sleep

from mpi4py import MPI

from data import some_list

# mpiexec -np 4 py parallel.py

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

count = len(some_list) // (size - 1)
offset = count * (rank - 1)

if rank == 0:
    start_time = time()
    responses = [comm.recv(source=proc_rank) for proc_rank in range(1, size)]
    print('final result is: {}'.format(sum(responses)))
    print('working time: {}'.format(time() - start_time))
else:
    result = 0
    for num in some_list[offset:offset+count]:
        result += num
        sleep(0.1)

    print('rank {} send result: {}'.format(rank, result))
    comm.send(result, dest=0)
