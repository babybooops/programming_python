import pygame

def draw_labyrinth(matrix, start, finish, width_line=20, width_walls=5, color_way=(255, 255, 255),
                   color_wall=(0, 0, 0),
                   border=5, color_start=(0, 255, 0), color_finish=(255, 0, 0)):
    width = (len(matrix) // 2 + 1) * width_line + (len(matrix) // 2) * width_walls + border * 2
    height = (len(matrix[0]) // 2 + 1) * width_line + (len(matrix[0]) // 2) * width_walls + border * 2
    for i in range(width):
        for j in range(height):
            if i < border or width - i <= border or j < border or height - j <= border:  # отображение границ лабиринта
                pygame.draw.line(window, color_wall, [i, j], [i, j], 1)
            else:
                if (i - border) % (width_line + width_walls) <= width_line:
                    x = (i - border) // (width_line + width_walls) * 2
                else:
                    x = (i - border) // (width_line + width_walls) * 2 + 1
                if (j - border) % (width_line + width_walls) <= width_line:
                    y = (j - border) // (width_line + width_walls) * 2
                else:
                    y = (j - border) // (width_line + width_walls) * 2 + 1
                if matrix[x][y]:
                    pygame.draw.line(window, color_way, [i, j], [i, j], 1)
                else:
                    pygame.draw.line(window, color_wall, [i, j], [i, j], 1)
    pygame.draw.rect(window, color_start, (
        border + start[0] * (width_line + width_walls), border + start[1] * (width_line + width_walls), width_line,
        width_line))
    pygame.draw.rect(window, color_finish, (
        border + finish[0] * (width_line + width_walls), border + finish[1] * (width_line + width_walls), width_line,
        width_line))