import pygame


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BLOCK_SIZE = 20
FPS = 10


WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
RED = (200, 0, 0)
DARK_RED = (100, 0, 0)  # яд
GREEN = (0, 200, 0)
BLUE = (0, 0, 255)     # Speed Boost
YELLOW = (255, 255, 0) # Slow Motion
CYAN = (0, 255, 255)   # Shield
GRAY = (100, 100, 100) # Препятствия

DB_CONFIG = {
    "dbname": "snake_db",
    "user": "postgres",
    "password": "AkcreGo1code_",
    "host": "localhost",
    "port": 5432
}
