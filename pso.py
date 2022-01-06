import random


def createParticle(lengthX, lengthY):
    matrix = [[int(random.randint(1, 3)/3) for i in range(lengthY)] for j in range(lengthY)]
    return matrix


def dealAlpha(rk):
    if rk < 0.001:
        return 10
    elif 0.1 > rk >= 0.001:
        return 20
    elif 0.1<= rk < 1:
        return 100
    else:
        return 300


def punish(zijks, lij):
    # rk

