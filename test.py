from multiprocessing.pool import ThreadPool
from random import random


# print(ts.get_hist_data())
# print(ts.get_suspended())
# print(ts.get_terminated())

def get_random(code):
    if code < .5:
        return code < .5


if __name__ == '__main__':
    tp = ThreadPool()
    r = tp.map(get_random, [random(), random(), random(), random()])
    print(r)
