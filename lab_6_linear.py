import os
import logging
import random
import time


# Run command
# mpiexec -np 2 py lab_5.py

RANDOM_MODE = True
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


def init_test_data():
    def generate_matrix():
        return [[random.randint(MIN_NUMBER, MAX_NUMBER) for _ in range(VECTORS_LEN)] for _ in range(VECTORS_LEN)]

    def get_matrix_width(matrix):
        lines_width = {len(line) for line in matrix}
        if len(lines_width) > 1:
            raise Exception('Incorrect matrix!')

        return list(lines_width)[0]

    if RANDOM_MODE:
        return generate_matrix(), generate_matrix()

    matrix_a = MATRIX_A
    matrix_b = MATRIX_B

    width_matrix_a = get_matrix_width(matrix_a)
    _ = get_matrix_width(matrix_b)
    if width_matrix_a != len(matrix_b):
        raise Exception('Cant multiple this matrix!')

    matrix_a_len = len(matrix_a)

    return matrix_a, matrix_b


def vector_multiply(vector_a, vector_b):
    return sum([vector_a[i] * vector_b[i] for i in range(len(vector_a))])


if __name__ == '__main__':
    matrix_a, matrix_b = init_test_data()

    start_time = time.time()

    result = [
        [vector_multiply(line_a, line_b) for line_b in zip(*matrix_b)]
        for line_a in matrix_a
    ]

    result_message = 'Result:'
    time_message = 'Time: {} ms'.format(round((time.time() - start_time) * 1000))
    print(result_message)
    print(*result, sep='\n')
    print(time_message)
