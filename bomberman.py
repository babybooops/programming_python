import random

def emptyMap(height: int, width: int) -> list:
    map = []
    c = '▓'
    map.append([])
    for i in range(width):
        map[0].append(c)
    for i in range(1, height - 1):
        map.append([])
        for j in range(width):
            if j == 0 or j == width - 1:
                map[i].append(c)
            else:
                map[i].append(' ')
    map.append([])
    for i in range(width):
        map[height - 1].append(c)
    return map


def obstaclesMap(height: int, width: int) -> list:
    height -= 2
    width -= 2
    map = []
    for i in range(height):
        map.append([])
        for j in range(width):
            if (i == 0 and j == 0) or (i == 1 and j == 0) or (i == 0 and j == 1):
                map[i].append(' ')
            elif (i == 0 and j == width - 1) or (i == 0 and j == width - 2) or (i == 1 and j == width - 1):
                map[i].append(' ')
            elif (i == height - 2 and j == 0) or (i == height - 1 and j == 0) or (i == height - 1 and j == 1):
                map[i].append(' ')
            elif (i == height - 1 and j == width - 2) or (i == height - 1 and j == width - 1) or (
                    i == height - 2 and j == width - 1):
                map[i].append(' ')
            elif (i % 2 == 1 and j % 2 == 1):
                map[i].append('▓')
            else:
                map[i].append(random.choice([' ', '░']))
    return map


def printMap(map: list, obstacles: list) -> None:
    for i in range(1, len(map) - 1):
        for j in range(1, len(map[i]) - 1):
            map[i][j] = obstacles[i - 1][j - 1]
    for i in range(len(map)):
        for j in range(len(map[i])):
            print(map[i][j], end='')
        print()
