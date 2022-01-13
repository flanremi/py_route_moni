import random
from Model import *

RANDOM_PATH_NUM = 100

# 定流变包,定包变流,跳数图,多端点
# idic = {CONSTANT_C: 1000, CONSTANT_F: 50, CONSTANT_DK: 150}
# imodel = Model(idic)
# # allocate_near = imodel.createTaskAllocate([
# #     xy2position(12, 30), xy2position(14, 41), xy2position(8, 29), xy2position(10, 21), xy2position(11, 33),
# #     xy2position(15, 38)])
# allocate_near = imodel.createTaskAllocate([
#     xy2position(0, 0), xy2position(0, 1), xy2position(1, 1), xy2position(1, 2), xy2position(2, 2),
#     xy2position(2, 3)])
# allocate_remote = imodel.createTaskAllocate([
#     xy2position(12, 30), xy2position(3, 13), xy2position(4, 55), xy2position(17, 15), xy2position(18, 57),
#     xy2position(8, 46)])


def checkRouteNum(pos, routes):
    p = getAdjArray(pos)
    s = 0
    for i in range(len(p)):
        if routes[imodel.get(MATRIX_2_LM)[pos][p[i]]] == 1:
            s += 1
    return s


# 建立连接的点，全部链路数组，全部点数组（用于查询链路连接数）
def BuildRandomRoute(pos, routes, points):
    p = getAdjArray(pos)
    candidates = []
    for i in range(len(p)):
        # 只和没有建立连接，且对方可以建立连接的点建立连接
        if routes[imodel.get(MATRIX_2_LM)[pos][p[i]]] == 0 and \
                points[p[i]] < 6:
            candidates.append(p[i])
    if len(candidates) == 0:
        return False
    i = random.randint(0, len(candidates) - 1)
    routes[imodel.get(MATRIX_2_LM)[pos][candidates[i]]] = 1
    # 更新连接两端端点的连接数
    points[pos] += 1
    points[candidates[i]] += 1
    return True


# 直接建立6条路径
def randomRoute():
    # [链路占用，建立链路数]
    ran_routes = [i for i in imodel.get(ARRAY_L)]
    points = [4 for i in range(imodel.get(CONSTANT_S))]
    for pos in range(imodel.get(CONSTANT_S)):
        while points[pos] < 6:
            if not BuildRandomRoute(pos, ran_routes, points):
                break
    return ran_routes


# 深度优先遍历，获得两点间的全部路径
def getPath(routes, start, end):
    path = []
    path_stack = [start]
    adj_stack = [imodel.getAdjArrayWithLink(start, routes)]
    (x1, y1) = position2xy(start)
    (x2, y2) = position2xy(end)
    path_shortest = (abs(x2 - x1) % SX + abs(y2 - y1) % SY) + 1
    while len(path_stack):
        adj_points = adj_stack[len(adj_stack) - 1]
        if len(adj_points) != 0:
            point = adj_points.pop(0)
            if point != end:
                # 避免环路
                is_cir = False
                for position in path_stack:
                    if point == position:
                        is_cir = True
                if is_cir:
                    continue
                # 若不是环路，则入栈
                # 限定路径长度，按理说两点间的最短路径长度应当尽可能接近于直接通路的距离，所以直接拒绝超过一定长度的路径进栈
                if len(path_stack) >= path_shortest:
                    continue
                path_stack.append(point)
                adj_stack.append(imodel.getAdjArrayWithLink(point, routes))
            else:
                # 若为终点，则path站即为一个解,将点翻译为链路后保存
                t_path = []
                for i in range(len(path_stack) - 1):
                    t_path.append(imodel.get(MATRIX_2_LM)[path_stack[i]][path_stack[i + 1]])
                t_path.append(imodel.get(MATRIX_2_LM)[path_stack[len(path_stack) - 1]][end])
                path.append(t_path)
                # if len(path) >= RANDOM_PATH_NUM:
                #     break
        else:
            # 若辅栈栈顶队列为空队列，即主站顶的节点已遍历完毕，已无可遍历，故，两者同时出栈
            path_stack.pop(len(path_stack) - 1)
            adj_stack.pop(len(adj_stack) - 1)
    return path


# 深度优先遍历，获得两点间的全部路径
def getPathPoint(routes, start, end):
    path = []
    path_stack = [start]
    adj_stack = [imodel.getAdjArrayWithLink(start, routes)]
    (x1, y1) = position2xy(start)
    (x2, y2) = position2xy(end)
    path_shortest = (abs(x2 - x1) % SX + abs(y2 - y1) % SY) + 1
    while len(path_stack):
        adj_points = adj_stack[len(adj_stack) - 1]
        if len(adj_points) != 0:
            point = adj_points.pop(0)
            if point != end:
                # 避免环路
                is_cir = False
                for position in path_stack:
                    if point == position:
                        is_cir = True
                if is_cir:
                    continue
                # 若不是环路，则入栈
                # 限定路径长度，按理说两点间的最短路径长度应当尽可能接近于直接通路的距离，所以直接拒绝超过一定长度的路径进栈
                if len(path_stack) >= path_shortest:
                    continue
                path_stack.append(point)
                adj_stack.append(imodel.getAdjArrayWithLink(point, routes))
            else:
                # 若为终点，则path站即为一个解,将点翻译为链路后保存
                t_path = []
                for i in range(len(path_stack)):
                    t_path.append(path_stack[i])
                t_path.append(end)
                path.append(t_path)
                # if len(path) >= RANDOM_PATH_NUM:
                #     break
        else:
            # 若辅栈栈顶队列为空队列，即主站顶的节点已遍历完毕，已无可遍历，故，两者同时出栈
            path_stack.pop(len(path_stack) - 1)
            adj_stack.pop(len(adj_stack) - 1)
    return path


def getResult():
    route = randomRoute()
    links = [0 for i in range(len(imodel.get(ARRAY_L)))]
    # 保存选择的路径
    tmp_path = []
    for (x, y, tasks) in imodel.allocate_near:
        paths = getPath(route, x, y)
        for i in range(tasks):
            path = paths[random.randint(0, len(paths) - 1)]
            tmp_path.append(path)
            for link in path:
                links[link] += 1
    max_used = 0
    for i in range(len(links)):
        if max_used <= links[i]:
            max_used = links[i]
    tmp_jump = 0
    for i in range(len(tmp_path)):
        tmp_jump += len(tmp_path[i])
    return max_used * imodel.get(CONSTANT_DK) / imodel.get(CONSTANT_C), tmp_jump / len(tmp_path)
    # print("最大信道占用率：" + str(max_used * imodel.get(CONSTANT_DK) / imodel.get(CONSTANT_C)))


# getResult()



def getRandomMatrix():
    matrix = [[[0, 0] for i in range(len(imodel.get(ARRAY_L)))] for j in range(imodel.get(CONSTANT_F))]
    routes = randomRoute()
    task_pos = 0
    for (x, y, tasks) in imodel.allocate_near:
        paths = getPathPoint(routes, x, y)
        for i in range(tasks):
            path = paths[random.randint(0, len(paths) - 1)]
            for j in range(len(path) - 1):
                if path[j] < path[j + 1]:
                    matrix[task_pos][imodel.get(MATRIX_2_LM)[path[j]][path[j+1]]][0] = 1
                else:
                    matrix[task_pos][imodel.get(MATRIX_2_LM)[path[j]][path[j+1]]][1] = 1
            task_pos += 1
    return matrix

# getRandomMatrix()
