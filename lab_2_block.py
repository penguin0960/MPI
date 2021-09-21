import logging

from mpi4py import MPI

# mpiexec -np 5 py lab_2_block.py

TAG = 2


def next_rank(cur_rank, size, step=1):
    return abs((cur_rank + step) % size)


logging.basicConfig(filename='logs\\' + __file__.split('\\')[-1][:-3] + '.log', level=logging.INFO)

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

logging.info('INIT {}'.format(rank))

if rank == 0:
    message = comm.sendrecv(
        sendobj=rank,
        dest=next_rank(rank, size),
        sendtag=TAG,
        source=next_rank(rank, size, step=-1),
        recvtag=TAG,
    )
    print(message)
else:
    logging.info('rank {} wait'.format(rank))

    message = comm.recv(
        source=next_rank(rank, size, step=-1),
        tag=TAG,
    )
    logging.info('rank {} got message: {}'.format(rank, message))

    comm.send(
        message+rank,
        dest=next_rank(rank, size),
        tag=TAG
    )
    logging.info('rank {} sent message: {}'.format(rank, message+rank))
