import os
import logging
import random
import time

from mpi4py import MPI

# Run command
# mpiexec -np 2 py lab_5.py

RANDOM_MODE = True
TAG = 2
MATRIX_A = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
]
MATRIX_B = [
    [0, 0, 0, 1],
    [3, 1, 2, 5],
    [2, 3, 1, 7],
]

VECTORS_LEN = 200
MIN_NUMBER = -100
MAX_NUMBER = 100

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


def init_test_data():
    def generate_matrix():
        return [[random.randint(MIN_NUMBER, MAX_NUMBER) for _ in range(VECTORS_LEN)] for _ in range(VECTORS_LEN)]

    def get_matrix_width(matrix):
        lines_width = {len(line) for line in matrix}
        if len(lines_width) > 1:
            raise Exception('Incorrect matrix!')

        return list(lines_width)[0]

    if RANDOM_MODE:
        return generate_matrix(), generate_matrix(), VECTORS_LEN // (size - 1)

    matrix_a = MATRIX_A
    matrix_b = MATRIX_B

    width_matrix_a = get_matrix_width(matrix_a)
    _ = get_matrix_width(matrix_b)
    if width_matrix_a != len(matrix_b):
        raise Exception('Cant multiple this matrix!')

    matrix_a_len = len(matrix_a)
    if size - 1 > matrix_a_len:
        raise Exception('Too many processes!')

    return matrix_a, matrix_b, matrix_a_len // (size - 1)


def vector_multiply(vector_a, vector_b):
    return sum([vector_a[i] * vector_b[i] for i in range(len(vector_a))])


if __name__ == '__main__':

    if rank == 0:
        matrix_a, matrix_b, matrix_split_len = init_test_data()

        start_time = time.time()
        matrix_for_send = []
        for proc_rank in range(1, size):
            if proc_rank == size - 1:
                matrix_for_send.append(matrix_a[matrix_split_len * (proc_rank - 1):])
            else:
                matrix_for_send.append(matrix_a[matrix_split_len * (proc_rank - 1): matrix_split_len * proc_rank])

        scatter_matrix = [None] + matrix_for_send
        logger.info(scatter_matrix)
        comm.scatter(
            sendobj=scatter_matrix,
            root=0,
        )
        comm.bcast(
            obj=list(zip(*matrix_b)),
            root=0,
        )
        # Получение результатов от процессов
        result = comm.gather(
            sendobj=None,
            root=0,
        )
        # Соединение результатов в общую матрицу
        result_matrix = []
        for line in result[1:]:
            result_matrix.extend(line)

        result_message = 'Result:'
        time_message = 'Time: {} ms'.format(round((time.time() - start_time) * 1000))
        print(result_message)
        print(*result_matrix, sep='\n')
        print(time_message)
    else:
        # Получение данных от 0 процесса
        fragment_from_a = comm.scatter(sendobj=None, root=0)

        if not RANDOM_MODE:
            print(f'{rank} A {fragment_from_a}')

        matrix_b = comm.bcast(obj=None, root=0)

        if not RANDOM_MODE:
            print(f'{rank} B {matrix_b}')

        result = [
            [vector_multiply(line_a, line_b) for line_b in matrix_b]
            for line_a in fragment_from_a
        ]
        comm.gather(
            sendobj=result,
            root=0,
        )
