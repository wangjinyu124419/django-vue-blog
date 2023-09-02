# -*- coding: utf-8 -*-
import time


def count_time(func):
    def wrapper(*arg, **kwargs):
        s_time = time.time()
        res = func(*arg, **kwargs)
        e_time = time.time()
        c_time = e_time - s_time
        print(f"函数{func.__name__}执行耗时:{int(c_time)}秒")
        return res

    return wrapper
