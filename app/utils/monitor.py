# coding=utf-8
"""
filename: monitor.py
author: zhancongc@icloud.com
description: cpu性能曲线
"""

import time
import threading
import psutil as ps
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def monitor_cpu(period):
    PERIOD = period
    times = 0
    t = list()
    cpu_percent = list()
    start_time = time.time()
    while times < PERIOD:
        t.append(time.time() - start_time)
        cpu_percent.append(ps.cpu_percent())
        # 清除所有活动坐标轴
        plt.clf()
        average_cpu_percent = sum(cpu_percent) / len(cpu_percent)
        plt.title("CPU performance, average: {0}%".format(round(average_cpu_percent, 2)))
        plt.xlabel("time(second)")
        plt.ylabel("cpu percent(%)")
        plt.ylim(0, 100)
        plt.plot(t, cpu_percent)
        plt.pause(0.1)
        times += 1
    print(cpu_percent)
    plt.savefig("./cpu_percent.png")


def monitor_memory(period):
    PERIOD = period
    times = 0
    t = list()
    memory_percent = list()
    start_time = time.time()
    while times < PERIOD:
        t.append(time.time() - start_time)
        memory_percent.append(ps.virtual_memory().percent)
        # 清除所有活动坐标轴
        plt.clf()
        average_memory_percent = sum(memory_percent) / len(memory_percent)
        plt.title("Memory performance, average: {0}%".format(round(average_memory_percent, 2)))
        plt.xlabel("time(second)")
        plt.ylabel("memory percent(%)")
        plt.ylim(0, 100)
        plt.plot(t, memory_percent)
        plt.pause(0.1)
        times += 1
    print(memory_percent)
    plt.savefig("./memory_percent.png")


if __name__ == "__main__":
    monitor_memory(100)





