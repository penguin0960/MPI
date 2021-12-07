import os
import logging
import random
import time
from math import log

from mpi4py import MPI

# Run command
# mpiexec -np 2 py lab_8.py

RANDOM_MODE = False
TAG = 2
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
GRAPH = [
    [0, 1, 0, 1],
    [1, 0, 1, 0],
    [0, 1, 0, 1],
    [1, 0, 1, 0],
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

    if size - 1 > width:
        raise Exception('Too many processes!')

    return matrix


if __name__ == '__main__':

    if rank == 0:
        graph = init_test_data()
        start_time = time.time()
        # Вычисляем размерность гиберкуба
        hibercube_rank = log(len(graph), 2)
        hibercube_rank = int(hibercube_rank) if hibercube_rank.is_integer() else None
        # Если получить не удалось (вершин в графе не 2^N), то работа программы прекращается сразу
        print(f'hibercube_rank: {hibercube_rank}')
        # Передаем каждому процессу размерность гиберкуба или сигнал прекращения работы
        comm.bcast(
            obj=hibercube_rank,
            root=0,
        )
        result = False
        if hibercube_rank is not None:
            matrix_split_len = len(graph) // (size - 1)
            matrix_for_send = []
            for proc_rank in range(1, size):
                if proc_rank == size - 1:
                    matrix_for_send.append(graph[matrix_split_len * (proc_rank - 1):])
                else:
                    matrix_for_send.append(graph[matrix_split_len * (proc_rank - 1): matrix_split_len * proc_rank])

            scatter_matrix = [None, *matrix_for_send]
            comm.scatter(
                sendobj=scatter_matrix,
                root=0,
            )

            # Получение результатов от процессов
            # LAND - Logical AND
            result = comm.reduce(
                sendobj=True,
                root=0,
                op=MPI.LAND,
            )

        result_message = f'Result: {result}'
        time_message = 'Time: {} ms'.format(round((time.time() - start_time) * 1000))
        print(result_message)
        print(time_message)
    else:
        # Получение размерности гиперкуба от 0 процесса
        # Если будет получен None, граф не может быть гиперкубом и работа программы на этом заканчивается
        hibercube_rank = comm.bcast(
            obj=None,
            root=0,
        )

        if hibercube_rank is not None:
            graph_fragment = comm.scatter(
                sendobj=None,
                root=0,
            )
            if not RANDOM_MODE:
                print(f'process {rank} get: {graph_fragment}')

            # Проверка количества ребер для каждой вершины
            answer = True
            for line in graph_fragment:
                logger.info(line)
                if sum(line) != hibercube_rank:
                    answer = False
                    logger.info('break')
                    break

            comm.reduce(
                sendobj=answer,
                root=0,
                op=MPI.LAND,
            )
            if not RANDOM_MODE:
                print(f'process {rank} send: {answer}')
