import pygame
from persistence2 import *
from racer2 import RacerGame
from config2 import *

pygame.init()
font = pygame.font.SysFont("Arial", 28)

def draw_center(screen, text, y, color=WHITE):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(SCREEN_WIDTH//2, y))
    screen.blit(surf, rect)

def main_menu(screen):
    username = "Player"
    settings = load_settings()
    while True:
        screen.fill(BLACK)
        draw_center(screen, "RACER TOP-DOWN", 120, YELLOW)
        draw_center(screen, f"User: {username}", 220)
        draw_center(screen, "[P] Play  [S] Settings  [L] Leaderboard  [Q] Quit", 320)
        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT: return
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_p:
                    game = RacerGame(screen, username, settings)
                    run_game(game)
                elif e.key == pygame.K_s: settings_screen(screen, settings)
                elif e.key == pygame.K_l: leaderboard_screen(screen)
                elif e.key == pygame.K_q: return
                elif e.key == pygame.K_BACKSPACE: username = username[:-1]
                else:
                    if len(username) < 10 and e.unicode.isprintable():
                        username += e.unicode

def settings_screen(screen, settings):
    running = True
    while running:
        screen.fill(BLACK)
        draw_center(screen, "SETTINGS", 120, YELLOW)
        draw_center(screen, f"1. Sound: {'On' if settings['sound'] else 'Off'}", 220)
        draw_center(screen, f"2. Car color: {tuple(settings['color'])}", 260)
        draw_center(screen, f"3. Difficulty: {settings['difficulty']}", 300)
        draw_center(screen, "[S] Save & Back", 420)
        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT: return
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_1:
                    settings['sound'] = not settings['sound']
                elif e.key == pygame.K_2:
                    import random
                    settings['color'] = [random.randint(0,255) for _ in range(3)]
                elif e.key == pygame.K_3:
                    settings['difficulty'] = "hard" if settings['difficulty']=="normal" else "normal"
                elif e.key == pygame.K_s:
                    save_settings(settings); running = False

def leaderboard_screen(screen):
    data = load_leaderboard()
    screen.fill(BLACK)
    draw_center(screen, "TOP 10 LEADERBOARD", 100, YELLOW)
    for i, r in enumerate(data):
        draw_center(screen, f"{i+1}. {r['user']} - {r['score']} pts - {r['distance']} m", 160 + i*30)
    draw_center(screen, "Press B to go back", 520)
    pygame.display.flip()

    waiting = True
    while waiting:
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN and e.key == pygame.K_b: waiting = False
            elif e.type == pygame.QUIT: waiting = False

def run_game(game):
    clock = pygame.time.Clock()
    while game.running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                game.running = False
        game.update()
        game.draw()
        pygame.display.flip()
        clock.tick(30)
