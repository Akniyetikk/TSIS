import pygame
import json
import db1
import random
from game1 import SnakeGame
from config1 import *

pygame.init()
db1.init_db()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 30)

def draw_text(text, y, color=WHITE):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(SCREEN_WIDTH//2, y))
    screen.blit(surf, rect)

def settings_screen():
    try:
        with open('settings1.json', 'r') as f: settings = json.load(f)
    except:
        settings = {"color": [0, 255, 0], "grid": True, "sound": True}
    
    running = True
    while running:
        screen.fill(BLACK)
        draw_text("SETTINGS", 100)
        draw_text(f"1. Grid: {'ON' if settings['grid'] else 'OFF'}", 200)
        draw_text(f"2. Color: {settings['color']}", 250)
        draw_text("Press S to Save & Back", 400)
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1: settings['grid'] = not settings['grid']
                if event.key == pygame.K_2: settings['color'] = [random.randint(0,255) for _ in range(3)]
                if event.key == pygame.K_s:
                    with open('settings1.json', 'w') as f: json.dump(settings, f)
                    running = False

def leaderboard_screen():
    running = True
    scores = db1.get_leaderboard()
    while running:
        screen.fill(BLACK)
        draw_text("TOP 10 LEADERBOARD", 50)
        for i, res in enumerate(scores):
            draw_text(f"{i+1}. {res[0]} - {res[1]} (Lvl {res[2]})", 120 + i*30)
        draw_text("Press B to Back", 500)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_b: running = False

def main_menu():
    username = "Player1"
    while True:
        screen.fill(BLACK)
        draw_text("SNAKE PRO MAX", 100, GREEN)
        draw_text(f"Name: {username} (Type to change)", 200)
        draw_text("P - Play | L - Leaderboard | S - Settings | Q - Quit", 350)
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    print("Попытка запуска игры...") 
                    try:
                        game = SnakeGame(username, screen)
                        game.run()
                    except Exception as e:
                         print(f"Ошибка при запуске: {e}") 
                    while game.update():
                        game.draw()
                        clock.tick(FPS + game.level + game.speed_mod)
                elif event.key == pygame.K_l: leaderboard_screen()
                elif event.key == pygame.K_s: settings_screen()
                elif event.key == pygame.K_q: return
                elif event.key == pygame.K_BACKSPACE: username = username[:-1]
                else: 
                    if len(username) < 10: username += event.unicode

if __name__ == "__main__":
    main_menu()
