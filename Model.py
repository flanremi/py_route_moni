# 链路容量矩阵
import random

CONSTANT_C = 'constant_c'
# 流数
CONSTANT_F = 'constant_f'
# 包的大小
CONSTANT_DK = 'constant_dk'
# 卫星个数
CONSTANT_S = 'constant_s'
# 全链路矩阵
ARRAY_L = 'array_l'
# 邻接矩阵
MATRIX_2_LM = 'matrix_2_lm'
# 流量大小
ARRAY_DK = 'array_dk'

SX = 8
SY = 14


def position2xy(pos: int):
    return int(pos / SY), pos % SY


def xy2position(x, y):
    return int(x * SY + y)


# 创建固定链路，并为所有链路添加序号
def createMartixLW():
    s = SX * SY
    # 定义
    matrix = [[-1 for i in range(s)] for j in range(s)]
    mapping = [-1 for i in range(s * 4)]
    k = 0
    for i in range(0, s):
        (x, y) = position2xy(i)
        p1 = xy2position(x, (y + 1) % SY)
        p2 = xy2position(x, (y + SY - 1) % SY)
        p3 = xy2position((x + SX - 1) % SX, (y + SY - 1) % SY)
        p4 = xy2position((x + 1) % SX, (y + 1) % SY)
        p5 = xy2position((x + 1) % SX, y)
        p6 = xy2position((x + SX - 1) % SX, y)
        p7 = xy2position((x + SX - 1) % SX, (y + 1) % SY)
        p8 = xy2position((x + 1) % SX, (y + SY - 1) % SY)
        p = [p1, p2, p3, p4, p5, p6, p7, p8]
        for j in range(0, 8):
            if i < p[j]:
                matrix[i][p[j]] = k
                matrix[p[j]][i] = k
                if j < 4:
                    mapping[k] = 1
                else:
                    mapping[k] = 0
                k += 1
    return matrix, mapping


def getAdjArray(position: int):
    (x, y) = position2xy(position)
    # 邻接8个卫星的序号
    # →
    p1 = xy2position(x, (y + 1) % SY)
    # ←
    p2 = xy2position(x, (y + SY - 1) % SY)
    # 左下
    p3 = xy2position((x + SX - 1) % SX, (y + SY - 1) % SY)
    # 右上
    p4 = xy2position((x + 1) % SX, (y + 1) % SY)
    # 上
    p5 = xy2position((x + 1) % SX, y)
    # 下
    p6 = xy2position((x + SX - 1) % SX, y)
    # 右下
    p7 = xy2position((x + SX - 1) % SX, (y + 1) % SY)
    # 左上
    p8 = xy2position((x + 1) % SX, (y + SY - 1) % SY)
    p = [p1, p2, p3, p4, p5, p6, p7, p8]
    return p


class Model(dict):

    def __init__(self, dic) -> None:
        super().__init__()
        # 修改dic
        self.update(dic)
        ms = createMartixLW()
        self.update({ARRAY_L: ms[1]})
        self.update({MATRIX_2_LM: ms[0]})
        self.update({CONSTANT_S: SX * SY})
        self.allocate_near = []
        self.allocate_remote = []

    def notify(self, dic):
        # 修改dic
        self.update(dic)
        ms = createMartixLW()
        self.update({ARRAY_L: ms[1]})
        self.update({MATRIX_2_LM: ms[0]})
        self.update({CONSTANT_S: SX * SY})

    # 返回（起，终，任务数）
    def createTaskAllocate(self, point: list):
        route = []
        remain = self.get(CONSTANT_F)
        road = int(len(point) * (len(point) - 1) / 2)
        for i in range(len(point)):
            for j in range(len(point)):
                if j > i:
                    tasknum = random.randint(0, int(remain / road * 2))
                    route.append((point[i], point[j], tasknum))
                    remain -= tasknum
                    road -= 1
        route[len(route) - 1] = (route[len(route) - 1][0], route[len(route) - 1][1], route[len(route) - 1][2] + remain)
        return route

    # 返回（起，终，任务数） 固定版
    def createTaskAllocateFix(self, point: list):
        route = []
        remain = self.get(CONSTANT_F)
        road = int(len(point) * (len(point) - 1) / 2)
        position = 0
        allocation = [3,5,1,2,7, 2,1,3,4,3, 5,3,4,2,5]
        for i in range(len(point)):
            for j in range(len(point)):
                if j > i:
                    route.append((point[i], point[j], allocation[position]))
                    position += 1
        # route[len(route) - 1] = (route[len(route) - 1][0], route[len(route) - 1][1], route[len(route) - 1][2] + remain)
        return route

    def link2position(self, l: int):
        for i in range(self.get(CONSTANT_S)):
            for j in range(self.get(CONSTANT_S)):
                if i > j:
                    continue
                if l == self.get(MATRIX_2_LM)[i][j]:
                    return i, j

    def getAdjArrayWithLink(self, position: int, routes):
        p = getAdjArray(position)
        remove_list = []
        for i in range(len(p)):
            if routes[self.get(MATRIX_2_LM)[position][p[i]]] == 0:
                remove_list.append(p[i])
        for i in range(len(remove_list)):
            for j in range(len(p)):
                if p[j] == remove_list[i]:
                    p.pop(j)
                    break
        return p

    def getU(self, matrix):
        links = [0 for i in range(len(self.get(ARRAY_L)))]
        for i in range(self.get(CONSTANT_F)):
            for j in range(len(self.get(ARRAY_L))):
                for k in range(2):
                    if matrix[i][j][0] == 1 or matrix[i][j][1] == 1:
                        links[j] += 1
        max_link = 0
        for link in links:
            if max_link <= link:
                max_link = link
        return max_link * self.get(CONSTANT_DK) / self.get(CONSTANT_C)


imodel = Model({CONSTANT_C: 1000, CONSTANT_DK: 150})
# 3 * 4
near_array = [xy2position(0, 0), xy2position(0, 1), xy2position(1, 1), xy2position(1, 2), xy2position(2, 2),
              xy2position(2, 3)]
# 8 * 14
remote_array = [xy2position(4, 7), xy2position(6, 10), xy2position(6, 2), xy2position(2, 12), xy2position(2, 3),
                xy2position(0, 0)]
# remote_array = [xy2position(4, 7),
#                 xy2position(0, 0)]
# imodel.createTaskAllocate([
# xy2position(0, 0), xy2position(0, 1), xy2position(1, 1), xy2position(1, 2), xy2position(2, 2),
# xy2position(2, 3)])

# imodel.createTaskAllocate([
# xy2position(12, 30), xy2position(3, 13), xy2position(4, 55), xy2position(17, 15), xy2position(18, 57),
# xy2position(8, 46)])
