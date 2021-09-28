import random

from mpi4py import MPI

# mpiexec -np 5 py lab_3.py

TAG = 2
MIN_NUMBER = -1000
MAX_NUMBER = 1000

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# data = []

if rank == 0:
    requests = [comm.irecv(source=process_rank, tag=TAG) for process_rank in (1, 2)]
    numbers_from_1, numbers_from_2 = MPI.Request.waitall(requests=requests)
    result = []
    while numbers_from_1 and numbers_from_2:
        if numbers_from_1[0] < numbers_from_2[0]:
            result.append(numbers_from_1.pop(0))
        else:
            result.append(numbers_from_2.pop(0))

    result.extend(numbers_from_1)
    result.extend(numbers_from_2)
    print('result: {}'.format(result))
elif rank in (1, 2):
    requests = [comm.irecv(source=process_rank, tag=TAG) for process_rank in range(rank + 2, size, 2)]
    received_numbers = MPI.Request.waitall(requests=requests)
    print('proc {} get list {}'.format(rank, received_numbers))
    sorted_numbers = sorted(received_numbers)
    send_request = comm.isend(
        obj=sorted_numbers,
        dest=0,
        tag=TAG,
    )
    print('proc {} sended list {}'.format(rank, sorted_numbers))
    send_request.wait()
else:
    number_for_send = random.randint(MIN_NUMBER, MAX_NUMBER)
    # number_for_send = data[rank - 3]
    send_to = (rank + 1) % 2 + 1
    send_request = comm.isend(
        obj=number_for_send,
        dest=send_to,
        tag=TAG,
    )
    print('proc {} send {} to {}'.format(rank, number_for_send, send_to))
    send_request.wait()
