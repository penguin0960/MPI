import os
import logging
import random
import time

from mpi4py import MPI

# Run command
# mpiexec -np 2 py lab_7.py

RANDOM_MODE = False
TAG = 2
# 25
# GRAPH = [
#     [0, 1, 1, 0, 0, 1, 0, 0, 0, 1],
#     [1, 0, 0, 0, 1, 1, 0, 0, 1, 1],
#     [1, 0, 0, 1, 1, 1, 1, 0, 0, 1],
#     [0, 0, 1, 0, 0, 0, 1, 1, 0, 0],
#     [0, 1, 1, 0, 0, 0, 0, 1, 1, 1],
#     [1, 1, 1, 0, 0, 0, 1, 0, 1, 1],
#     [0, 0, 1, 1, 0, 1, 0, 1, 1, 1],
#     [0, 0, 0, 1, 1, 0, 1, 0, 0, 0],
#     [0, 1, 0, 0, 1, 1, 1, 0, 0, 1],
#     [1, 1, 1, 0, 1, 1, 1, 0, 1, 0],
# ]
# 2
GRAPH = [
    [0, 1, 1],
    [1, 0, 0],
    [1, 0, 0],
]

GRAPH_SIZE = 100

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
    def generate_matrix(matrix_size):
        return [[random.randint(0, 1) for _ in range(matrix_size)] for _ in range(matrix_size)]

    def get_random_graph(graph_size):
        graph = generate_matrix(graph_size)
        for i in range(graph_size):
            for j in range(graph_size):
                if i == j:
                    graph[i][j] = 0
                    continue

                graph[i][j] = graph[j][i]

        return graph

    def get_matrix_width(matrix):
        lines_width = {len(line) for line in matrix}
        if len(lines_width) > 1:
            raise Exception('Incorrect matrix!')

        return list(lines_width)[0]

    if RANDOM_MODE:
        return get_random_graph(GRAPH_SIZE)

    matrix = GRAPH

    width = get_matrix_width(matrix)
    if width != len(matrix):
        raise Exception('Not correct matrix!')

    if size > width:
        raise Exception('Too many processes!')

    return matrix


if __name__ == '__main__':

    if rank == 0:
        graph = init_test_data()
        formatted_graph_matrix = [
            [x for x in line[:index]]
            for index, line in enumerate(graph[1:], 1)
        ]
        matrix_split_len = len(formatted_graph_matrix) // (size - 1)

        start_time = time.time()
        matrix_for_send = []
        for proc_rank in range(1, size):
            if proc_rank == size - 1:
                matrix_for_send.append(formatted_graph_matrix[matrix_split_len * (proc_rank - 1):])
            else:
                matrix_for_send.append(formatted_graph_matrix[matrix_split_len * (proc_rank - 1): matrix_split_len * proc_rank])

        scatter_matrix = [None, *matrix_for_send]
        comm.scatter(
            sendobj=scatter_matrix,
            root=0,
        )

        # Получение результатов от процессов
        # Сумма в reduce по умолчанию
        result = comm.reduce(
            sendobj=0,
            root=0,
        )

        result_message = f'Result: {result}'
        time_message = 'Time: {} ms'.format(round((time.time() - start_time) * 1000))
        print(result_message)
        print(time_message)
    else:
        # Получение данных от 0 процесса
        graph_fragment = comm.scatter(sendobj=None, root=0)

        if not RANDOM_MODE:
            print(f'{rank} A {graph_fragment}')

        result = sum(
            [
                sum(line)
                for line in graph_fragment
            ]
        )
        comm.reduce(
            sendobj=result,
            root=0,
        )
