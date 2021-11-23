import os
import logging
import random
import time

import numpy
from mpi4py import MPI

from mpi_utils import MPI_Isend, MPI_Ssend, MPI_Issend, MPI_Bsend, MPI_Ibsend, MPI_Rsend, MPI_Irsend, MPI_Send

# Run command
# mpiexec -np 2 py lab_5.py

SEND_MODE = 's'
VECTORS_MODE = 'RANDOM'
TAG = 2
VECTOR_A = [1, 2, 3, 4, 5, 1]
VECTOR_B = [1, 1, 1, 1, 2, 1]

VECTORS_LEN = 100
MIN_NUMBER = -1000
MAX_NUMBER = 1000

file_name = os.path.basename(__file__)
logger = logging.getLogger(file_name)
logging.basicConfig(
    filename='logs/logs.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()


def send_message(comm: MPI.Intracomm, **kwargs):
    if SEND_MODE == 'i':
        return MPI_Isend(comm=comm, **kwargs)
    if SEND_MODE == 's':
        return MPI_Ssend(comm=comm, **kwargs)
    if SEND_MODE == 'is':
        return MPI_Issend(comm=comm, **kwargs)
    if SEND_MODE == 'b':
        return MPI_Bsend(comm=comm, **kwargs)
    if SEND_MODE == 'ib':
        return MPI_Ibsend(comm=comm, **kwargs)
    if SEND_MODE == 'r':
        return MPI_Rsend(comm=comm, **kwargs)
    if SEND_MODE == 'ir':
        return MPI_Irsend(comm=comm, **kwargs)

    return MPI_Send(comm=comm, **kwargs)


def recv(comm: MPI.Intracomm, **kwargs):
    if 'i' in SEND_MODE:
        return comm.irecv(**kwargs)

    return comm.recv(**kwargs)


if VECTORS_MODE == 'RANDOM':
    vectors_len = VECTORS_LEN
    vector_a = numpy.array([random.randint(MIN_NUMBER, MAX_NUMBER) for _ in range(vectors_len)])
    vector_b = numpy.array([random.randint(MIN_NUMBER, MAX_NUMBER) for _ in range(vectors_len)])
else:
    vectors_len = len(VECTOR_A)
    vector_a = numpy.array(VECTOR_A)
    vector_b = numpy.array(VECTOR_B)

if len(VECTOR_A) != len(VECTOR_B):
    raise Exception('Vectors has different lengths')

if size - 1 > vectors_len:
    raise Exception('Too many processes')


if __name__ == '__main__':
    vector_split_len = vectors_len // (size - 1)
    if rank == 0:
        start_time = time.time()
        print('Vector A: {}'.format(vector_a))
        print('Vector B: {}'.format(vector_b))

        # Разбиение векторов на части для процессов
        for proc_rank in range(1, size):
            if proc_rank == size - 1:
                fragment_from_a = vector_a[vector_split_len * (proc_rank - 1):]
                fragment_from_b = vector_b[vector_split_len * (proc_rank - 1):]
            else:
                fragment_from_a = vector_a[vector_split_len * (proc_rank - 1): vector_split_len * proc_rank]
                fragment_from_b = vector_b[vector_split_len * (proc_rank - 1): vector_split_len * proc_rank]

            # Сборка векторов в один и отправка
            # fragment_for_send = numpy.array(list(fragment_from_a) + list(fragment_from_b))
            fragment_for_send = list(fragment_from_a) + list(fragment_from_b)
            send_request = send_message(
                comm=comm,
                obj=fragment_for_send,
                dest=proc_rank,
                tag=TAG,
            )
            if isinstance(send_request, MPI.Request):
                send_request.wait()

            logger.info('Sent message to {}: {}'.format(proc_rank, fragment_for_send))

        # Получение результатов от процессов и вычисление скалярного произведения
        result = 0
        for proc_rank in range(1, size):
            buffer = numpy.arange(1)
            answer = recv(comm=comm, source=proc_rank, tag=TAG)
            if isinstance(answer, MPI.Request):
                answer = answer.wait()

            logger.info('Recv message from {}: {}'.format(proc_rank, answer))
            result += answer[0]

        result_message = 'Result: {}'.format(result)
        time_message = 'Time: {} seconds'.format(time.time() - start_time)
        print(result_message)
        logger.info(result_message)
        print(time_message)
        logger.warning(time_message)
    else:
        # Получение данных от 0 процесса
        answer = recv(comm=comm, source=0, tag=TAG)
        if isinstance(answer, MPI.Request):
            answer = answer.wait()

        answer_middle_index = len(answer) // 2
        fragment_from_a = answer[:answer_middle_index]
        fragment_from_b = answer[answer_middle_index:]

        result = 0
        for coord_a, coord_b in zip(fragment_from_a, fragment_from_b):
            result += coord_a * coord_b

        number_for_send = numpy.array([result])
        send_request = send_message(
            comm=comm,
            obj=number_for_send,
            dest=0,
            tag=TAG,
        )
        if isinstance(send_request, MPI.Request):
            send_request.wait()
