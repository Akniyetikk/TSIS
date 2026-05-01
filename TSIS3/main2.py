import pygame
from ui2 import main_menu
from config2 import *

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Top-Down Racer")
    main_menu(screen)
    pygame.quit()
