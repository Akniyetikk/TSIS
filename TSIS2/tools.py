import pygame
from collections import deque


def flood_fill(surface, x, y, new_color):
    target_color = surface.get_at((x, y))
    if target_color == new_color: return
    
    queue = deque([(x, y)])
    width, height = surface.get_size()
    
    while queue:
        curr_x, curr_y = queue.popleft()
        if surface.get_at((curr_x, curr_y)) != target_color:
            continue
        
        surface.set_at((curr_x, curr_y), new_color)
        
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = curr_x + dx, curr_y + dy
            if 0 <= nx < width and 0 <= ny < height:
                queue.append((nx, ny))


def draw_rect(surface, color, start_pos, end_pos, width):
    rect = pygame.Rect(start_pos, (end_pos[0] - start_pos[0], end_pos[1] - start_pos[1]))
    pygame.draw.rect(surface, color, rect, width)

def draw_circle(surface, color, start_pos, end_pos, width):
    center = start_pos
    radius = int(((end_pos[0] - start_pos[0])**2 + (end_pos[1] - start_pos[1])**2)**0.5)
    pygame.draw.circle(surface, color, center, radius, width)

import pygame
from collections import deque
import math

def draw_poly(surface, color, points, width):
    pygame.draw.polygon(surface, color, points, width)

def draw_square(surface, color, start, end, width):
    side = max(abs(end[0] - start[0]), abs(end[1] - start[1]))
    rect = pygame.Rect(start[0], start[1], side, side)
    pygame.draw.rect(surface, color, rect, width)

def draw_right_triangle(surface, color, start, end, width):
    points = [start, (start[0], end[1]), end]
    draw_poly(surface, color, points, width)

def draw_equilateral_triangle(surface, color, start, end, width):
    side = end[0] - start[0]
    height = side * math.sqrt(3) / 2
    points = [start, (end[0], start[1]), (start[0] + side/2, start[1] + height)]
    draw_poly(surface, color, points, width)

def draw_rhombus(surface, color, start, end, width):
    center_x = (start[0] + end[0]) / 2
    center_y = (start[1] + end[1]) / 2
    points = [
        (center_x, start[1]), (end[0], center_y),
        (center_x, end[1]), (start[0], center_y)
    ]
    draw_poly(surface, color, points, width)
