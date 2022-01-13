import json
import os
import sys

import matplotlib
from matplotlib import pyplot as plt
from linear import *
from comparable import *
from pso import *
from Model import *
from multiprocessing import Pool

matplotlib.use("Agg")


# 小范围
def drawSmallPic():
    colors = ["#ADC9C3", "#6F9B91", "#F0BAC5", "#E38597", "#C05D78", "#FA4436", "#FF0000"]
    u1 = []
    u2 = []
    u3 = []
    t_y = [i for i in range(10, 50)]
    for f in range(10, 50):
        imodel.update({CONSTANT_F: f})
        imodel.allocate_near = imodel.createTaskAllocate(near_array)
        u1.append(linearOpt(imodel)[0])
        u2.append(getResult()[0])
        u3.append(update2()[0])
    plt.plot(t_y, u1, c=colors[0])
    plt.plot(t_y, u2, c=colors[1])
    plt.plot(t_y, u3, c=colors[2])
    # plt.xlabel('某一时刻卫星网络中流的数量')
    # plt.ylabel('卫星网络的最大负载的链路利用率 ')
    # # plt.legend(loc='upper left')
    # plt.title('Comparison Diagram of\nthe Power and the Capacity')
    plt.savefig(".svg", format='svg')


def collectData(type: int):
    colors = ["#ADC9C3", "#6F9B91", "#F0BAC5", "#E38597", "#C05D78", "#FA4436", "#FF0000"]
    # 小范围，动任务数，不动大小
    if type == 0:
        u1 = []
        u2 = []
        u3 = []
        x = [i for i in range(10, 50)]
        imodel.update({CONSTANT_DK: 150})
        for f in range(10, 50):
            imodel.update({CONSTANT_F: f})
            imodel.allocate_near = imodel.createTaskAllocate(near_array)
            u1.append(linearOpt(imodel)[0])
            u2.append(getResult()[0])
            u3.append(update2()[0])
        x = [i for i in range(10, 50)]
        plt.plot(x, u1, c=colors[1])
        plt.plot(x, u2, c=colors[2])
        plt.plot(x, u3, c=colors[3])
        plt.xlabel('the Number of Flows')
        plt.ylabel('the largest Utilization Rate of Links')
        plt.savefig("small_dkc_fd.svg", format='svg')
    # 小范围，不动任务数，动大小
    elif type == 1:
        u1 = []
        u2 = []
        u3 = []
        imodel.update({CONSTANT_F: 50})
        for f in range(1, 41):
            imodel.update({CONSTANT_DK: f * 2 + 70})
            imodel.allocate_near = imodel.createTaskAllocate(near_array)
            u1.append(linearOpt(imodel)[0])
            u2.append(getResult()[0])
            u3.append(update2()[0])
        x = [i * 2 + 70 for i in range(1, 41)]
        plt.plot(x, u1, c=colors[1])
        plt.plot(x, u2, c=colors[2])
        plt.plot(x, u3, c=colors[3])
        plt.xlabel('the Size of Flows')
        plt.ylabel('the largest Utilization Rate of Links')
        plt.savefig("small_fc_dkd.svg", format='svg')
        # with open('\\small_fc_dkd\\result0', 'w') as file:
        #     file.write(json.dumps({'u1': u1, 'u2': u2, 'u3': u3}))
    # 大范围，动任务数，不动大小
    elif type == 2:
        u1 = []
        u2 = []
        u3 = []
        imodel.notify({})
        imodel.update({CONSTANT_DK: 150})

        def func2(fn):
            imodel.update({CONSTANT_F: fn})
            imodel.allocate_near = imodel.createTaskAllocate(remote_array)
            result = str(linearOpt(imodel)[0]) + " " + str(getResult()[0]) + " " + str(update2()[0])
            with open("big_dkc_fd/" + str(fn), "w") as file:
                file.write(result)

        pool = Pool(processes=37)
        pool.map(func2, range(13, 51))
        # for f in range(10, 50):
        #     imodel.update({CONSTANT_F: f})
        #     imodel.allocate_near = imodel.createTaskAllocate(remote_array)
        #     u1.append(linearOpt(imodel)[0])
        #     u2.append(getResult()[0])
        #     u3.append(update2()[0])
        # x = [i for i in range(10, 50)]
        # plt.plot(x, u1, c=colors[1])
        # plt.plot(x, u2, c=colors[2])
        # plt.plot(x, u3, c=colors[3])
        # plt.xlabel('the Number of Flows')
        # plt.ylabel('the largest Utilization Rate of Links')
        # plt.savefig("big_dkc_fd.svg", format='svg')
        # with open('\\big_dkc_fd\\result0', 'w') as file:
        #     file.write(json.dumps({'u1': u1, 'u2': u2, 'u3': u3}))
    # 大范围，定任务数，动大小
    elif type == 3:
        u1 = []
        u2 = []
        u3 = []
        imodel.update({CONSTANT_F: 50})
        for f in range(1, 41):
            imodel.update({CONSTANT_DK: f * 2 + 70})
            imodel.allocate_near = imodel.createTaskAllocate(remote_array)
            u1.append(linearOpt(imodel)[0])
            u2.append(getResult()[0])
            u3.append(update2()[0])
        x = [i * 2 + 70 for i in range(1, 41)]
        plt.plot(x, u1, c=colors[1])
        plt.plot(x, u2, c=colors[2])
        plt.plot(x, u3, c=colors[3])
        plt.xlabel('the Size of Flows')
        plt.ylabel('the largest Utilization Rate of Links')
        plt.savefig("big_fc_dkd.svg", format='svg')
        # with open('\\big_fc_dkd\\result0', 'w') as file:
        #     file.write(json.dumps({'u1': u1, 'u2': u2, 'u3': u3}))


def run():
    imodel.notify({})
    imodel.update({CONSTANT_DK: 150})

    def func2(fn):
        imodel.update({CONSTANT_F: fn})
        imodel.allocate_near = imodel.createTaskAllocate(remote_array)
        result = str(linearOpt(imodel)[0]) + " " + str(getResult()[0]) + " " + str(update2()[0])
        with open("big_dkc_fd/" + str(fn), "w") as file:
            file.write(result)

    pool = Pool(processes=77)
    pool.map(func2, range(13, 51))

    imodel.notify({})
    imodel.update({CONSTANT_F: 50})
    imodel.allocate_near = imodel.createTaskAllocate(remote_array)

    def func3(dkn):
        imodel.update({CONSTANT_DK: dkn * 2 + 70})
        result = str(linearOpt(imodel)[0]) + " " + str(getResult()[0]) + " " + str(update2()[0])
        with open("big_fc_dkd/" + str(dkn), "w") as file:
            file.write(result)

    pool.map(func3, range(1, 41))


run()