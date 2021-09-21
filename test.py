import logging
from time import time, sleep

from mpi4py import MPI

# mpiexec -np 2 py test.py

TAG = 2


def next_rank(cur_rank, size, step=1):
    return abs((cur_rank + step) % size)


comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

logging.basicConfig(filename='logs\\' + __file__.split('\\')[-1][:-3] + '.log', level=logging.INFO)
logging.info('INIT {}'.format(rank))
some = 0

if rank == 0:
    logging.info('rank {} started'.format(rank))
    comm.Send([b'0', MPI.INT], dest=1, tag=TAG)
    logging.info('rank {} send'.format(rank))
    some_message = comm.recv()
    logging.info('rank {} recv'.format(rank))
    comm.send(some, dest=1, tag=TAG)
    logging.info('rank {} send'.format(rank))

else:
    logging.info('rank {} started'.format(rank))
    buf = [b'\0', MPI.INT]
    comm.Recv(buf)
    print(buf)
    logging.info('rank {} recv'.format(rank))
    comm.send(some, dest=0, tag=TAG)
    logging.info('rank {} send'.format(rank))
    some_message = comm.recv()
    logging.info('rank {} recv'.format(rank))
