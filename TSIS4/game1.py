import pygame
import random
import json
import db1
from config1 import *

class SnakeGame:
    def __init__(self, username, screen):
        self.screen = screen
        self.username = username
        self.player_id = db1.get_player_id(username)
        self.font = pygame.font.SysFont("Arial", 22)
        self.load_settings()
        self.reset_game()

    def load_settings(self):
        try:
            with open('settings1.json', 'r') as f:
                self.settings = json.load(f)
        except:
            self.settings = {"color": GREEN, "grid": True, "sound": True}

    def reset_game(self):
        self.snake = [[100, 100], [80, 100], [60, 100]]
        self.direction = "RIGHT"
        self.score = 0
        self.level = 1
        self.speed_mod = 0
        self.has_shield = False
        self.obstacles = []
        
        self.power_up = None
        self.active_effects = {}
        
        self.spawn_food()
        self.spawn_poison()

    def spawn_food(self):
        while True:
            pos = [random.randrange(0, SCREEN_WIDTH//BLOCK_SIZE)*BLOCK_SIZE, 
                   random.randrange(0, SCREEN_HEIGHT//BLOCK_SIZE)*BLOCK_SIZE]
            if pos not in self.snake and pos not in self.obstacles:
                self.food = pos; break

    def spawn_poison(self):
        while True:
            pos = [random.randrange(0, SCREEN_WIDTH//BLOCK_SIZE)*BLOCK_SIZE, 
                   random.randrange(0, SCREEN_HEIGHT//BLOCK_SIZE)*BLOCK_SIZE]
            if pos not in self.snake and pos != self.food and pos not in self.obstacles:
                self.poison = pos; break

    def spawn_power_up(self):
        if self.power_up: return
        types = ["SPEED", "SLOW", "SHIELD"]
        while True:
            pos = [random.randrange(0, SCREEN_WIDTH//BLOCK_SIZE)*BLOCK_SIZE, 
                   random.randrange(0, SCREEN_HEIGHT//BLOCK_SIZE)*BLOCK_SIZE]
            if pos not in self.snake and pos != self.food and pos not in self.obstacles:
                self.power_up = {"pos": pos, "type": random.choice(types), "time": pygame.time.get_ticks()}
                break

    def handle_power_ups(self):
        now = pygame.time.get_ticks()
        if self.power_up and now - self.power_up["time"] > 8000:
            self.power_up = None
        
        if not self.power_up and random.random() < 0.02:
            self.spawn_power_up()

        for effect in list(self.active_effects.keys()):
            if now > self.active_effects[effect]:
                if effect == "SPEED" or effect == "SLOW": self.speed_mod = 0
                del self.active_effects[effect]

    def update(self):
        self.handle_power_ups()
        
        head = self.snake[0][:]
        if self.direction == "UP": head[1] -= BLOCK_SIZE
        elif self.direction == "DOWN": head[1] += BLOCK_SIZE
        elif self.direction == "LEFT": head[0] -= BLOCK_SIZE
        elif self.direction == "RIGHT": head[0] += BLOCK_SIZE

        collision = False
        if head[0] < 0 or head[0] >= SCREEN_WIDTH or head[1] < 0 or head[1] >= SCREEN_HEIGHT or head in self.snake or head in self.obstacles:
            if self.has_shield:
                self.has_shield = False
                return True 
            else:
                collision = True

        if collision:
            db1.save_game_result(self.player_id, self.score, self.level)
            return False

        self.snake.insert(0, head)

        if head == self.food:
            self.score += 1
            if self.score % 5 == 0:
                self.level += 1
                if self.level >= 3: self.add_obstacles()
            self.spawn_food()
        elif head == self.poison:
            self.spawn_poison()
            for _ in range(2): 
                if len(self.snake) > 1: self.snake.pop()
            if len(self.snake) <= 1: return False
        elif self.power_up and head == self.power_up["pos"]:
            p_type = self.power_up["type"]
            now = pygame.time.get_ticks()
            if p_type == "SPEED":
                self.speed_mod = 5
                self.active_effects["SPEED"] = now + 5000
            elif p_type == "SLOW":
                self.speed_mod = -3
                self.active_effects["SLOW"] = now + 5000
            elif p_type == "SHIELD":
                self.has_shield = True
            self.power_up = None
        else:
            self.snake.pop()
        
        return True

    def add_obstacles(self):
        for _ in range(3):
            while True:
                obs = [random.randrange(0, SCREEN_WIDTH//BLOCK_SIZE)*BLOCK_SIZE, 
                       random.randrange(0, SCREEN_HEIGHT//BLOCK_SIZE)*BLOCK_SIZE]
                dist = abs(obs[0] - self.snake[0][0]) + abs(obs[1] - self.snake[0][1])
                if obs not in self.snake and obs != self.food and dist > BLOCK_SIZE * 2:
                    self.obstacles.append(obs)
                    break

    def draw(self):
        self.screen.fill(BLACK)
        if self.settings["grid"]:
            for x in range(0, SCREEN_WIDTH, BLOCK_SIZE):
                pygame.draw.line(self.screen, (40, 40, 40), (x, 0), (x, SCREEN_HEIGHT))
        
        color = CYAN if self.has_shield else self.settings["color"]
        for pos in self.snake:
            pygame.draw.rect(self.screen, color, (pos[0], pos[1], BLOCK_SIZE-1, BLOCK_SIZE-1))
        
        pygame.draw.rect(self.screen, RED, (self.food[0], self.food[1], BLOCK_SIZE, BLOCK_SIZE))
        pygame.draw.rect(self.screen, DARK_RED, (self.poison[0], self.poison[1], BLOCK_SIZE, BLOCK_SIZE))
        for obs in self.obstacles:
            pygame.draw.rect(self.screen, GRAY, (obs[0], obs[1], BLOCK_SIZE, BLOCK_SIZE))
            
        if self.power_up:
            p_color = BLUE if self.power_up["type"] == "SPEED" else YELLOW if self.power_up["type"] == "SLOW" else CYAN
            pygame.draw.ellipse(self.screen, p_color, (self.power_up["pos"][0], self.power_up["pos"][1], BLOCK_SIZE, BLOCK_SIZE))

        txt = self.font.render(f"Score: {self.score}  Lvl: {self.level}  User: {self.username}", True, WHITE)
        self.screen.blit(txt, (10, 10))

    def run(self):
        """Главный цикл игры"""
        clock = pygame.time.Clock()
        running = True
        while running:
            speed = 10 + self.level + self.speed_mod
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and self.direction != "DOWN":
                        self.direction = "UP"
                    elif event.key == pygame.K_DOWN and self.direction != "UP":
                        self.direction = "DOWN"
                    elif event.key == pygame.K_LEFT and self.direction != "RIGHT":
                        self.direction = "LEFT"
                    elif event.key == pygame.K_RIGHT and self.direction != "LEFT":
                        self.direction = "RIGHT"

            
            if not self.update():
                running = False 
            

            self.draw()
            pygame.display.flip()
            
            clock.tick(speed)
