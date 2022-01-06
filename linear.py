import json
import random

from Model import *
import pulp

# 定流变包,定包变流,跳数图,多端点
idic = {CONSTANT_C: 1000, CONSTANT_F: 50, CONSTANT_DK: 150}
imodel = Model(idic)
# allocate_near = imodel.createTaskAllocate([
#     xy2position(12, 30), xy2position(14, 41), xy2position(8, 29), xy2position(10, 21), xy2position(11, 33),
#     xy2position(15, 38)])
allocate_near = imodel.createTaskAllocate([
    xy2position(0, 0), xy2position(0, 1), xy2position(1, 1), xy2position(1, 2), xy2position(2, 2),
    xy2position(2, 3)])
allocate_remote = imodel.createTaskAllocate([
    xy2position(12, 30), xy2position(3, 13), xy2position(4, 55), xy2position(17, 15), xy2position(18, 57),
    xy2position(8, 46)])


def loadFDK(n, dic: dict):
    dks = []
    for i in range(n):
        pass


def checkup(zijk, links):
    for k in range(imodel.get(CONSTANT_F)):
        for j in range(len(imodel.get(ARRAY_L))):
            for i in range(2):
                if zijk[k][j][i] > links[j]:
                    print("链路" + str(j) + "异常")
    for pos in range(imodel.get(CONSTANT_S)):
        p = getAdjArray(pos)
        s = 0
        for i in range(len(p)):
            # pos-pi链路的序号
            l = imodel.get(MATRIX_2_LM)[pos][p[i]]
            s += links[l]
        # print(str(p) + str(pos) + ":有" + str(s) + "条链路")
        if s > 6:
            print(str(p) + str(pos) + ":错误，有" + str(s) + "条链路 > 6")
    ls = [0 for i in range(len(imodel.get(ARRAY_L)))]
    for k in range(imodel.get(CONSTANT_F)):
        for j in range(len(imodel.get(ARRAY_L))):
            for i in range(2):
                if zijk[k][j][i] == 1:
                    ls[j] +=1
    max_l = 0
    for l in ls:
        if l >= max_l:
            max_l = l
    print(max_l)


def linearOpt(dic):
    global imodel
    imodel.update(dic)
    prob = pulp.LpProblem("route", pulp.LpMinimize)
    u = pulp.LpVariable("miu", 0, 1)
    prob += u, "Z"
    variables_l = []
    # [任务k][l][方向]，定义0为序号小到序号大，1位序号大到序号小
    variables_z = [
        [[pulp.LpVariable('z' + str(j) + '_' + str(k) + "_" + str(i), 0, 1, cat=pulp.LpInteger) for i in range(2)]
         for j in range(len(imodel.get(ARRAY_L)))]
        for k in range(imodel.get(CONSTANT_F))]
    for i in range(len(imodel.get(ARRAY_L))):
        variables_l.append(pulp.LpVariable('l' + str(i), 0, 1, cat=pulp.LpInteger))
        # c5
        prob += variables_l[i] >= imodel.get(ARRAY_L)[i]
    # c6
    for pos in range(imodel.get(CONSTANT_S)):
        p = getAdjArray(pos)
        s = 0
        for i in range(len(p)):
            # pos-pi链路的序号
            l = imodel.get(MATRIX_2_LM)[pos][p[i]]
            s += variables_l[l]
        prob += s <= 6
    for k in range(imodel.get(CONSTANT_F)):
        for i in range(len(imodel.get(ARRAY_L))):
            for j in range(2):
                # c4
                prob += variables_z[k][i][j] <= variables_l[i]
    # c1
    for i in range(len(imodel.get(ARRAY_L))):
        s = 0
        for k in range(imodel.get(CONSTANT_F)):
            for j in range(2):
                s += variables_z[k][i][j]
        prob += s * imodel.get(CONSTANT_DK) <= u * imodel.get(CONSTANT_C)
    # c7 c8,task记录已经安排的任务数
    task = 0
    for i in range(len(allocate_near)):
        (start, end, tasks) = allocate_near[i]
        for j in range(tasks):
            p = getAdjArray(start)
            outs = 0
            ins = 0
            for k in range(len(p)):
                # 起点周围必有一条通路
                if start < p[k]:
                    outs += variables_z[task][imodel.get(MATRIX_2_LM)[start][p[k]]][0]
                    ins += variables_z[task][imodel.get(MATRIX_2_LM)[start][p[k]]][1]
                else:
                    outs += variables_z[task][imodel.get(MATRIX_2_LM)[start][p[k]]][1]
                    ins += variables_z[task][imodel.get(MATRIX_2_LM)[start][p[k]]][0]
            prob += outs == 1
            prob += ins == 0
            p = getAdjArray(end)
            outs = 0
            ins = 0
            for k in range(len(p)):
                # 终点周围必有一条通路, 终点看的是入度，和起点是相反的，需注意
                if end > p[k]:
                    outs += variables_z[task][imodel.get(MATRIX_2_LM)[end][p[k]]][1]
                    ins += variables_z[task][imodel.get(MATRIX_2_LM)[end][p[k]]][0]
                else:
                    outs += variables_z[task][imodel.get(MATRIX_2_LM)[end][p[k]]][0]
                    ins += variables_z[task][imodel.get(MATRIX_2_LM)[end][p[k]]][1]
            prob += outs == 0
            prob += ins == 1
            task += 1
    # c9  i+j一共遍历100次，等同于遍历任务队列 补：若限制中间点，每个点的出入度都为1，则可以解决环路的问题
    task = 0
    for i in range(len(allocate_near)):
        (start, end, tasks) = allocate_near[i]
        for j in range(tasks):
            # tar对应论文中的i
            for tar in range(imodel.get(CONSTANT_S)):
                if tar == start or tar == end:
                    continue
                # 左边累加
                p = getAdjArray(tar)
                left = 0
                for adj in range(len(p)):
                    if tar < p[adj]:
                        left += variables_z[task][imodel.get(MATRIX_2_LM)[tar][p[adj]]][0]
                    else:
                        left += variables_z[task][imodel.get(MATRIX_2_LM)[tar][p[adj]]][1]
                # 右边累加
                right = 0
                for adj in range(len(p)):
                    if tar > p[adj]:
                        right += variables_z[task][imodel.get(MATRIX_2_LM)[tar][p[adj]]][0]
                    else:
                        right += variables_z[task][imodel.get(MATRIX_2_LM)[tar][p[adj]]][1]
                prob += right == left
            task += 1
    solver = pulp.GUROBI_CMD()
    prob.solve(solver=solver)
    result_z = [[[0 for i in range(2)] for j in range(len(imodel.get(ARRAY_L)))] for k in range(imodel.get(CONSTANT_F))]
    for k in range(imodel.get(CONSTANT_F)):
        for j in range(len(imodel.get(ARRAY_L))):
            for i in range(2):
                result_z[k][j][i] = variables_z[k][j][i].value()
    result = []
    for k in range(imodel.get(CONSTANT_F)):
        routes = []
        for j in range(len(imodel.get(ARRAY_L))):
            for i in range(2):
                route = variables_z[k][j][i].value()
                if route == 1:
                    (x, y) = imodel.link2position(j)
                    if x > y:
                        a = y
                        b = x
                    else:
                        a = x
                        b = y
                    if i == 0:
                        routes.append((a, b))
                    else:
                        routes.append((b, a))
        result.append(routes)
    print(result)
    print(allocate_near)
    result_l = []
    for i in range(len(variables_l)):
        result_l.append(variables_l[i].value())
    checkup(result_z, result_l)
    print(u.value())


linearOpt({})
# print(pulp.list_solvers(onlyAvailable=True))


