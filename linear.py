from time import time, sleep

from data import some_list

start_time = time()
result = 0
for num in some_list:
    result += num
    # sleep(0.1)

print('final result is: {}'.format(result))
print('working time: {}'.format(time() - start_time))
print()
