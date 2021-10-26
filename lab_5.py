import logging
import random
import time

import numpy
from mpi4py import MPI

# mpiexec -np 2 py lab_5.py

SEND_MODE = 'DEFAULT'
VECTOR_A = [1, 2, 3, 4, 5]
VECTOR_B = [1, 1, 1, 1, 2]
VECTORS_LEN = 10000

TAG = 2
MIN_NUMBER = -1000
MAX_NUMBER = 1000


def send(comm: MPI.Intracomm, **kwargs):
    if SEND_MODE == 'R':
        return comm.Rsend(**kwargs)
    if SEND_MODE == 'b':
        return comm.bsend(**kwargs)
    if SEND_MODE == 'B':
        return comm.Bsend(**kwargs)
    if SEND_MODE == 's':
        return comm.ssend(**kwargs)
    if SEND_MODE == 'S':
        return comm.Ssend(**kwargs)
    if SEND_MODE == 'i':
        return comm.isend(**kwargs)

    return comm.send(**kwargs)


comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

logging.basicConfig(filename='logs\\' + __file__.split('\\')[-1][:-3] + '.log', level=logging.INFO)

# if len(VECTOR_A) != len(VECTOR_B):
#     raise Exception()

vectors_len = len(VECTOR_A)
# vectors_len = VECTORS_LEN
vector_split_len = vectors_len // (size - 1)

if size - 1 > vectors_len:
    raise Exception('Too many processes')

# vector_a = numpy.array([random.randint(MIN_NUMBER, MAX_NUMBER) for _ in range(vectors_len)])
# vector_b = numpy.array([random.randint(MIN_NUMBER, MAX_NUMBER) for _ in range(vectors_len)])
vector_a = numpy.array(VECTOR_A)
vector_b = numpy.array(VECTOR_B)

if rank == 0:
    print('Vector A: {}'.format(vector_a))
    print('Vector B: {}'.format(vector_b))
    start_time = time.time()
    for proc_rank in range(1, size):
        if proc_rank == size - 1:
            fragmend_from_a = vector_a[vector_split_len * (proc_rank - 1):]
            fragmend_from_b = vector_b[vector_split_len * (proc_rank - 1):]
        else:
            fragmend_from_a = vector_a[vector_split_len * (proc_rank - 1): vector_split_len * proc_rank]
            fragmend_from_b = vector_b[vector_split_len * (proc_rank - 1): vector_split_len * proc_rank]

        fragment_for_send = numpy.array(list(fragmend_from_a) + list(fragmend_from_b))
        logging.info('bsend {}'.format(fragment_for_send))
        comm.Send(buf=fragment_for_send, dest=proc_rank, tag=TAG)
        logging.info('sended {}'.format(fragment_for_send))
        print('Proc {} sent message: {}'.format(rank, fragment_for_send))

    result = 0
    for proc_rank in range(1, size):
        buffer = numpy.arange(1)
        comm.Recv(buf=buffer, source=proc_rank, tag=TAG)
        print('Proc {} got message: {}'.format(rank, buffer))
        result += buffer[0]

    print('Result: {}'.format(result))
    print('Time: {} seconds'.format(time.time() - start_time))
else:
    buffer_len = vector_split_len * 2
    if rank == size - 1:
        buffer_len += (vectors_len % (size - 1)) * 2

    buffer = numpy.arange(buffer_len)
    comm.Recv(buf=buffer, source=0, tag=TAG)
    logging.info('recv {}'.format(buffer))
    print('Proc {} got message: {}'.format(rank, buffer))
    fragment_from_a = buffer[:buffer_len // 2]
    fragment_from_b = buffer[buffer_len // 2:]

    result = 0
    for coord_a, coord_b in zip(fragment_from_a, fragment_from_b):
        result += coord_a * coord_b

    number_for_send = numpy.array([result])
    comm.Send(buf=number_for_send, dest=0, tag=TAG)
    print('Proc {} sent message: {}'.format(rank, number_for_send))
