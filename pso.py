import math
import random
from comparable import *

from Model import *

# idic = {CONSTANT_C: 1000, CONSTANT_F: 50, CONSTANT_DK: 150}
# imodel = Model(idic)
# allocate_near = imodel.createTaskAllocate([
#     xy2position(12, 30), xy2position(14, 41), xy2position(8, 29), xy2position(10, 21), xy2position(11, 33),
#     xy2position(15, 38)])
# allocate_near = imodel.createTaskAllocate([
#     xy2position(0, 0), xy2position(0, 1), xy2position(1, 1), xy2position(1, 2), xy2position(2, 2),
#     xy2position(2, 3)])
# allocate_remote = imodel.createTaskAllocate([
#     xy2position(12, 30), xy2position(3, 13), xy2position(4, 55), xy2position(17, 15), xy2position(18, 57),
#     xy2position(8, 46)])

iterator_max = 50
particle_num = 100


def createParticle(lengthX, lengthY):
    matrix = [[[random.randint(1, 30000) / 30000, random.randint(1, 30000) / 30000] for i in range(lengthY)] for j in
              range(lengthX)]
    return matrix


def dealAlpha(rk):
    if rk < 0.001:
        return 10
    elif 0.1 > rk >= 0.001:
        return 20
    elif 0.1 <= rk < 1:
        return 100
    else:
        return 300


def dealBeta(rk):
    if rk < 1:
        return 1
    else:
        return 2


def punish(t_matrix: list):
    global imodel

    def rk(num):
        if num <= 0:
            return 0
        else:
            return num

    matrix = [[[0, 0] for j in range(len(imodel.get(ARRAY_L)))] for i in range(imodel.get(CONSTANT_F))]
    # 处理matrix，离散化
    for j in range(len(imodel.get(ARRAY_L))):
        for i in range(imodel.get(CONSTANT_F)):
            for k in range(2):
                if t_matrix[i][j][k] >= 0.5:
                    matrix[i][j][k] = 1

    # rk
    links = [0 for i in range(len(imodel.get(ARRAY_L)))]
    for j in range(len(imodel.get(ARRAY_L))):
        for i in range(imodel.get(CONSTANT_F)):
            for k in range(2):
                if matrix[i][j][0] == 1 or matrix[i][j][1] == 1:
                    links[j] += 1
                    break
    max_link = 0
    for link in links:
        if max_link <= link:
            max_link = link
    rk1 = rk(imodel.get(CONSTANT_DK) * max_link / imodel.get(CONSTANT_C) - 1)
    # ==========通路6条===============
    t_link_sum = 0
    for position in range(imodel.get(CONSTANT_S)):
        ps = getAdjArray(position)
        t_links = 0
        for p in ps:
            for k in range(imodel.get(CONSTANT_F)):
                link = imodel.get(MATRIX_2_LM)[position][p]
                if matrix[k][link][0] == 1 or matrix[k][link][1] == 1:
                    t_links += 1
                    break
        if t_links > 6:
            t_link_sum += t_links - 6
    rk2 = rk(t_link_sum)
    # ==========起终点出入度===============
    t_link_sum = 0
    task_pos = 0
    for (start, end, task) in imodel.allocate_near:
        for k in range(task):
            start_in = 0
            start_out = 0
            end_in = 0
            end_out = 0
            start_ps = getAdjArray(start)
            for point in start_ps:
                if start < point:
                    start_out += matrix[task_pos][imodel.get(MATRIX_2_LM)[start][point]][0]
                    start_in += matrix[task_pos][imodel.get(MATRIX_2_LM)[start][point]][1]
                else:
                    start_out += matrix[task_pos][imodel.get(MATRIX_2_LM)[start][point]][1]
                    start_in += matrix[task_pos][imodel.get(MATRIX_2_LM)[start][point]][0]
            end_ps = getAdjArray(end)
            for point in end_ps:
                if end > point:
                    end_out += matrix[task_pos][imodel.get(MATRIX_2_LM)[end][point]][1]
                    end_in += matrix[task_pos][imodel.get(MATRIX_2_LM)[end][point]][0]
                else:
                    end_out += matrix[task_pos][imodel.get(MATRIX_2_LM)[end][point]][0]
                    end_in += matrix[task_pos][imodel.get(MATRIX_2_LM)[end][point]][1]
            t_link_sum += abs(start_out - 1) + abs(start_in) + abs(end_out) + abs(end_in - 1)
            task_pos += 1
    rk3 = rk(t_link_sum)
    # =========================
    t_link_sum = 0
    task = 0
    for i in range(len(imodel.allocate_near)):
        (start, end, tasks) = imodel.allocate_near[i]
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
                        left += matrix[task][imodel.get(MATRIX_2_LM)[tar][p[adj]]][0]
                    else:
                        left += matrix[task][imodel.get(MATRIX_2_LM)[tar][p[adj]]][1]
                # 右边累加
                right = 0
                for adj in range(len(p)):
                    if tar > p[adj]:
                        right += matrix[task][imodel.get(MATRIX_2_LM)[tar][p[adj]]][0]
                    else:
                        right += matrix[task][imodel.get(MATRIX_2_LM)[tar][p[adj]]][1]
                t_link_sum += abs(right - left)
            task += 1
    rk4 = rk(t_link_sum)
    # ===========无回路==============
    t_link_sum = 0
    for i in range(imodel.get(CONSTANT_F)):
        for j in range(len(imodel.get(ARRAY_L))):
            if matrix[i][j][0] == 1 and matrix[i][j][1] == 1:
                t_link_sum += 1
    rk5 = rk(t_link_sum)
    # =========================
    Hx = dealAlpha(rk1) * math.pow(rk1, dealBeta(rk1)) + dealAlpha(rk2) * math.pow(rk2, dealBeta(rk2)) + \
         dealAlpha(rk3) * math.pow(rk3, dealBeta(rk3)) + dealAlpha(rk4) * math.pow(rk4, dealBeta(rk4)) + \
         dealAlpha(rk5) * math.pow(rk5, dealBeta(rk5))
    return Hx


def get_fx(matrix: list):
    links = [0 for i in range(len(imodel.get(ARRAY_L)))]
    for i in range(imodel.get(CONSTANT_F)):
        for j in range(len(imodel.get(ARRAY_L))):
            for k in range(2):
                links[j] += matrix[i][j][k]
    max_link = 0
    for i in range(len(links)):
        if max_link <= links[i]:
            max_link = links[i]
    return max_link * imodel.get(CONSTANT_DK) / imodel.get(CONSTANT_C)


def getFx(matrix: list, i):
    t_matrix = [[[0, 0] for j in range(len(imodel.get(ARRAY_L)))] for i in range(imodel.get(CONSTANT_F))]
    # 处理matrix，离散化
    for link in range(len(imodel.get(ARRAY_L))):
        for task in range(imodel.get(CONSTANT_F)):
            for direct in range(2):
                if matrix[task][link][direct] >= 0.5:
                    t_matrix[task][link][direct] = 1
    # return get_fx(t_matrix) + (i * (i ** 0.5)) * punish(t_matrix)
    return get_fx(t_matrix) + punish(t_matrix)


def getW(i):
    w0 = 15
    wend = 2
    return w0 - (w0 - wend) * i / iterator_max


def update():
    c0 = 0.5
    c1 = 0.3
    c2 = 0.7
    matrixs = [createParticle(imodel.get(CONSTANT_F), len(imodel.get(ARRAY_L))) for i in range(particle_num)]
    matrixs[0] = getRandomMatrix()
    matrixs[1] = getRandomMatrix()
    matrixs[2] = getRandomMatrix()
    # [matrix] 上一次的速度
    # vPD = [[[[0, 0] for i in range(len(imodel.get(ARRAY_L)))] for j in range(imodel.get(CONSTANT_F))] for k in range(particle_num)]
    vPD = [[[[0, 0] for i in range(len(imodel.get(ARRAY_L)))] for j in range(imodel.get(CONSTANT_F))] for i in
           range(particle_num)]
    # 存储每次迭代过程中最佳结果的矩阵[适应值,矩阵]
    x_best = [[999999999999, []] for i in range(particle_num)]
    u_best = [999999999999, []]
    for i in range(1, iterator_max + 1):
        # 全局最优解
        # 预处理所有矩阵信息
        for j in range(len(matrixs)):
            u = getFx(matrixs[j], i)
            if u < x_best[j][0]:
                x_best[j] = [u, matrixs[j]]
            if u < u_best[0]:
                u_best[0] = u
                u_best[1] = matrixs[j]
        for j in range(len(x_best)):
            if x_best[j][0] < u_best[0]:
                u_best[0] = x_best[j][0]
                u_best[1] = x_best[j][1]
        for particle in range(particle_num):
            for task in range(imodel.get(CONSTANT_F)):
                for link in range(len(imodel.get(ARRAY_L))):
                    for direct in range(2):
                        xp = matrixs[particle][task][link][direct]
                        vPD[particle][task][link][direct] = c0 * (getW(i) * vPD[particle][task][link][direct] +
                                                                  c1 * random.randint(0, 10000) / 10000 *
                                                                  (x_best[particle][1][task][link][direct] - xp) +
                                                                  c2 * random.randint(0, 10000) / 10000 *
                                                                  (u_best[1][task][link][direct] - xp))
                        # 变动每一个zijk
                        matrixs[particle][task][link][direct] = xp + vPD[particle][task][link][direct]
            # xp = getFx(matrixs[particle], i)
            # vPD[particle] = c0 * (getW(i) * vPD[particle] + c1 * random.randint(0, 10000) / 10000 *
            #                       (x_best[particle][0] - xp) +
            #                       c2 * random.randint(0, 10000) / 10000 *
            #                       (u_best[0] - xp))
            # if abs(vPD[particle]) > 4:
            #     vPD[particle] = 4
            # # 整体平移
            # t_matrix = [[[0, 0] for i in range(len(imodel.get(ARRAY_L)))] for j in range(imodel.get(CONSTANT_F))]
            # for task in range(imodel.get(CONSTANT_F)):
            #     for link in range(len(imodel.get(ARRAY_L))):
            #         for direct in range(2):
            #             link_float = int(link + int(vPD[particle]) / 2) % len(imodel.get(ARRAY_L))
            #             direct_float = (direct + int(vPD[particle]) % 2) % 2
            #             t_matrix[task][link_float][direct_float] = matrixs[particle][task][link][direct]
            # matrixs[particle] = t_matrix
        print(u_best[0])
        t = []
        for (ux, mat) in x_best:
            t.append(ux)
        print(t)
        print(i)


# 基于路径的更新
def update2():
    c0 = 0.9
    c1 = 0.8
    c2 = 1.4
    routes = randomRoute()
    pathSs = [[[] for i in range(imodel.get(CONSTANT_S))] for j in range(imodel.get(CONSTANT_S))]
    particles = [[] for i in range(particle_num)]
    for part in range(particle_num):
        position = 0
        particle = [[] for i in range(imodel.get(CONSTANT_F))]
        for (start, end, task) in imodel.allocate_near:
            pathSs[start][end] = getPath(routes, start, end)
            for t in range(task):
                particle[position] = [start, end, pathSs[start][end][random.randint(0, len(pathSs[start][end]) - 1)]]
                position += 1
        particles[part] = particle

    def punishPart(p):
        links = [0 for i in range(len(imodel.get(ARRAY_L)))]
        for i in range(imodel.get(CONSTANT_F)):
            for j in range(len(p[i][2])):
                links[p[i][2][j]] += 1
        max_link = 0
        for link in links:
            if max_link < link:
                max_link = link
        return max_link * imodel.get(CONSTANT_DK) / imodel.get(CONSTANT_C)

    x_best = [[999999, []] for i in range(particle_num)]
    u_best = [999999, []]
    vPD = [[0 for j in range(imodel.get(CONSTANT_F))] for i in
           range(particle_num)]
    for i in range(1, iterator_max + 1):
        # 全局最优解
        # 预处理所有矩阵信息
        for j in range(len(particles)):
            u = punishPart(particles[j])
            if u < x_best[j][0]:
                x_best[j] = [u, particles[j]]
            if u < u_best[0]:
                u_best[0] = u
                u_best[1] = particles[j]
        for j in range(len(x_best)):
            if x_best[j][0] < u_best[0]:
                u_best[0] = x_best[j][0]
                u_best[1] = x_best[j][1]
        for particle in range(particle_num):
            for task in range(imodel.get(CONSTANT_F)):
                xp = pathSs[particles[particle][task][0]][particles[particle][task][1]] \
                    .index(particles[particle][task][2])
                vPD[particle][task] = c0 * (getW(i) * vPD[particle][task] +
                                            c1 * random.randint(0, 10000) / 10000 *
                                            (pathSs[x_best[particle][1][task][0]][x_best[particle][1][task][1]]
                                             .index(x_best[particle][1][task][2]) - xp) +
                                            c2 * random.randint(0, 10000) / 10000 *
                                            (pathSs[u_best[1][task][0]][u_best[1][task][1]]
                                             .index(u_best[1][task][2]) - xp))
                if 0.5 < abs(vPD[particle][task]) < 1:
                    if vPD[particle][task] < 0:
                        vPD[particle][task] = -1
                    else:
                        vPD[particle][task] = 1
                if abs(vPD[particle][task]) > 4:
                    if vPD[particle][task] < 0:
                        vPD[particle][task] = -4
                    else:
                        vPD[particle][task] = 4
                particles[particle][task][2] = pathSs[particles[particle][task][0]][particles[particle][task][1]][
                    int((xp + vPD[particle][task])) % len(
                        pathSs[particles[particle][task][0]][particles[particle][task][1]])]
    tmp_jump = 0
    for i in range(len(u_best[1])):
        tmp_jump += len(u_best[1][i][2])
    return u_best[0], tmp_jump / len(u_best[1][2])
