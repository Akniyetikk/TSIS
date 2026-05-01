import pygame
import random
import json
from persistence2 import save_leaderboard_entry
from config2 import *


class RacerGame:
    def __init__(self, screen, username, settings):
        self.screen = screen
        self.username = username
        self.settings = settings
        self.reset_game()
        self.font = pygame.font.SysFont("Arial", 22)
        if self.settings.get("sound", True):
            pygame.mixer.init()
            self.pickup_snd = pygame.mixer.Sound("pickup.wav") if "pickup.wav" in SOUND_FILES else None

    def reset_game(self):
        self.car = pygame.Rect(SCREEN_WIDTH // 2 - 25, SCREEN_HEIGHT - 120, 50, 90)
        self.traffic = []
        self.obstacles = []
        self.powerups = []
        self.active_power = None
        self.power_timer = 0
        self.speed = 8
        self.score = 0
        self.distance = 0
        self.has_shield = False
        self.running = True
        self.track_length = 1000
        self.last_spawn_y = 0  # безопасная дистанция между спаунами

    def get_occupied_lanes(self):
        """Возвращает список полос, где уже есть объекты вблизи верха экрана"""
        occupied = set()
        for rect in self.traffic:
            if -150 < rect.y < 200:
                occupied.add(rect.x)
        for rect, _ in self.obstacles:
            if -150 < rect.y < 200:
                occupied.add(rect.x)
        for rect, _ in self.powerups:
            if -150 < rect.y < 200:
                occupied.add(rect.x)
        return occupied

    def spawn_traffic(self):
        if len(self.traffic) < 5 and random.random() < 0.03:
            # спауним только если от последнего >= 250px по вертикали
            if self.traffic and abs(self.traffic[-1].y - self.last_spawn_y) < 250:
                return
            occupied = self.get_occupied_lanes()
            free = [lane for lane in LANES if lane not in occupied]
            if free:
                lane = random.choice(free)
                rect = pygame.Rect(lane, -120, 50, 90)
                self.traffic.append(rect)
                self.last_spawn_y = rect.y

    def spawn_obstacle(self):
        if random.random() < 0.01 and len(self.obstacles) < 3:
            occupied = self.get_occupied_lanes()
            free_lanes = [lane for lane in LANES if lane not in occupied]
            if free_lanes:
                lane = random.choice(free_lanes)
                rect = pygame.Rect(lane, -80, 60, 60)
                self.obstacles.append((rect, random.choice(["oil", "barrier"])))

    def spawn_powerup(self):
        if random.random() < 0.01 and not self.powerups:
            occupied = self.get_occupied_lanes()
            free_lanes = [lane for lane in LANES if lane not in occupied]
            if free_lanes:
                lane = random.choice(free_lanes)
                rect = pygame.Rect(lane, -80, 60, 60)
                p_type = random.choice(["Nitro", "Shield", "Repair"])
                self.powerups.append((rect, p_type))

    def handle_powerup_collision(self, p_type):
        now = pygame.time.get_ticks()
        if p_type == "Nitro":
            self.active_power = ("Nitro", now + 4000)
            self.speed = min(10 + self.score // 10, 18)
        elif p_type == "Shield":
            self.has_shield = True
        elif p_type == "Repair":
            self.score += 10
        self.powerups.clear()

    def update_powerups(self):
        if self.active_power:
            name, until = self.active_power
            if pygame.time.get_ticks() > until:
                if name == "Nitro":
                    self.speed -= 4
                self.active_power = None

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.car.left > ROAD_LEFT:
            self.car.x -= 8
        if keys[pygame.K_RIGHT] and self.car.right < ROAD_RIGHT:
            self.car.x += 8

        self.distance += self.speed / 10
        if self.distance >= self.track_length:
            self.distance = self.track_length
            self.running = False
            save_leaderboard_entry(self.username, self.score, int(self.distance))
            return

        self.score = int(self.distance // 5)

        for rect in self.traffic:
            rect.y += self.speed
        for rect, _ in self.obstacles:
            rect.y += self.speed
        for rect, _ in self.powerups:
            rect.y += self.speed * 0.8

        self.traffic = [t for t in self.traffic if t.y < SCREEN_HEIGHT]
        self.obstacles = [o for o in self.obstacles if o[0].y < SCREEN_HEIGHT]
        self.powerups = [p for p in self.powerups if p[0].y < SCREEN_HEIGHT]

        self.spawn_traffic()
        self.spawn_obstacle()
        self.spawn_powerup()
        self.update_powerups()
        self.check_collisions()

    def check_collisions(self):
        for rect in list(self.traffic):
            if self.car.colliderect(rect):
                if self.has_shield:
                    self.has_shield = False
                    self.traffic.remove(rect)
                else:
                    self.game_over()

        for rect, t in list(self.obstacles):
            if self.car.colliderect(rect):
                if t == "barrier":
                    if not self.has_shield:
                        self.game_over()
                    else:
                        self.obstacles.remove((rect, t))
                        self.has_shield = False
                else:
                    self.speed = max(3, self.speed - 2)
                    self.obstacles.remove((rect, t))

        for rect, p_type in list(self.powerups):
            if self.car.colliderect(rect):
                self.handle_powerup_collision(p_type)

    def game_over(self):
        save_leaderboard_entry(self.username, self.score, int(self.distance))
        self.running = False

    def draw(self):
        self.screen.fill(GRAY_ROAD)
        pygame.draw.rect(self.screen, DARK_GRAY, (ROAD_LEFT - 10, 0, 10, SCREEN_HEIGHT))
        pygame.draw.rect(self.screen, DARK_GRAY, (ROAD_RIGHT, 0, 10, SCREEN_HEIGHT))

        pygame.draw.rect(self.screen, self.settings.get("color", BLUE), self.car)

        for rect in self.traffic:
            pygame.draw.rect(self.screen, RED, rect)

        for rect, t in self.obstacles:
            color = BLACK if t == "oil" else ORANGE
            pygame.draw.rect(self.screen, color, rect)

        for rect, p_type in self.powerups:
            color = YELLOW if p_type == "Nitro" else CYAN if p_type == "Shield" else GREEN
            pygame.draw.ellipse(self.screen, color, rect)

        remaining = int(self.track_length - self.distance)
        if remaining < 0:
            remaining = 0

        text = self.font.render(
            f"{self.username}  Score:{self.score}  Dist:{int(self.distance)}m  Left:{remaining}m",
            True, WHITE,
        )
        self.screen.blit(text, (10, 10))

        if self.has_shield:
            shield_txt = self.font.render("🛡 Shield active", True, CYAN)
            self.screen.blit(shield_txt, (10, 40))

        if self.active_power and self.active_power[0] == "Nitro":
            boost_txt = self.font.render("Nitro Boost!", True, YELLOW)
            self.screen.blit(boost_txt, (10, 70))

        pygame.display.flip()
