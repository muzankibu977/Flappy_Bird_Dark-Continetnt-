import pygame
import random
import sys
import json
import os
import math

pygame.init()
pygame.mixer.init()

# Constants
MAIN_MENU = "main_menu"
GET_USERNAME = "get_username"
PLAYING = "playing"
PAUSED = "paused"
GAME_OVER = "game_over"
HIGH_SCORES = "high_scores"
SETTINGS = "settings"
INSTRUCTIONS = "instructions"
HIGH_SCORE_FILE = "highscores.json"
BOARD_WIDTH = 2048
BOARD_HEIGHT = 1024
BIRD_WIDTH = 34
BIRD_HEIGHT = 24
PIPE_WIDTH = 64
PIPE_HEIGHT = 512
COIN_WIDTH = 32
COIN_HEIGHT = 32

# Try loading a spooky font, fall back to Arial if not found
try:
    TITLE_FONT = pygame.font.Font("flappybirdtitlefont.ttf", 80)
except FileNotFoundError:
    TITLE_FONT = pygame.font.SysFont("Arial", 80)

FONT = pygame.font.SysFont("Arial", 32)
SMALL_FONT = pygame.font.SysFont("Arial", 24)
TINY_FONT = pygame.font.SysFont("Arial", 16)


def load_high_scores():
    if os.path.exists(HIGH_SCORE_FILE):
        with open(HIGH_SCORE_FILE, "r") as f:
            return json.load(f)
    return []


def save_high_scores(high_scores):
    with open(HIGH_SCORE_FILE, "w") as f:
        json.dump(high_scores, f)


def update_high_scores(name, score, high_scores):
    high_scores.append({"name": name, "score": score})
    high_scores.sort(key=lambda x: x["score"], reverse=True)
    return high_scores[:10]


class Bird:
    def __init__(self, img, x, y, width, height):
        self.img = img
        self.x = x
        self.y = y
        self.width = width
        self.height = height


class Coin:
    def __init__(self, img, x, y, width, height):
        self.img = img
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rotation = 0
        self.rotation_speed = 5


class Pipe:
    def __init__(self, img, x, y, width, height, is_moving=False):
        self.img = img
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.passed = False
        self.is_moving = is_moving
        self.movement_range = 50
        self.direction = 1
        self.speed = 1

    def update(self):
        if self.is_moving:
            self.y += self.direction * self.speed
            if abs(self.y % (2 * self.movement_range) - self.movement_range) > self.movement_range - 1:
                self.direction *= -1


class Slider:
    def __init__(self, x, y, w, h, min_val, max_val, initial_val):
        self.rect = pygame.Rect(x, y, w, h)
        self.knob_rect = pygame.Rect(x, y - 5, 20, h + 10)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.dragging = False
        self.update_knob_pos()

    def update_knob_pos(self):
        knob_x = self.rect.x + (self.val - self.min_val) / (self.max_val - self.min_val) * self.rect.width
        self.knob_rect.centerx = knob_x

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.knob_rect.collidepoint(event.pos):
                self.dragging = True
            elif self.rect.collidepoint(event.pos):
                self.val = self.min_val + (event.pos[0] - self.rect.x) / self.rect.width * (self.max_val - self.min_val)
                self.val = max(self.min_val, min(self.max_val, self.val))
                self.update_knob_pos()
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.val = self.min_val + (event.pos[0] - self.rect.x) / self.rect.width * (self.max_val - self.min_val)
            self.val = max(self.min_val, min(self.max_val, self.val))
            self.update_knob_pos()
            return True
        return False

    def draw(self, screen):
        pygame.draw.rect(screen, (100, 100, 100), self.rect)
        pygame.draw.rect(screen, (200, 200, 200), self.knob_rect)


class FlappyBirdGame:
    def __init__(self, screen):
        self.screen = screen
        self.bird_x = BOARD_WIDTH // 8
        self.bird_y = BOARD_HEIGHT // 2
        self.score = 0
        self.game_over = False
        self.velocity_x = -4
        self.velocity_y = 0
        self.gravity = 1
        self.pipe_interval = 1500
        self.last_pipe_time = pygame.time.get_ticks()
        self.pipes = []
        self.coins = []
        self.difficulty_level = 0
        self.user_name = ""
        self.volume = 0.5
        self.brightness = 1.0
        self.control_scheme = "space"  # "space", "mouse", "up_arrow"
        self.music_playing = True
        self.load_images()
        self.load_sounds()
        self.bird = Bird(self.bird_img, self.bird_x, self.bird_y, BIRD_WIDTH, BIRD_HEIGHT)
        self.bg_x1 = 0
        self.bg_x2 = BOARD_WIDTH
        self.bg_speed = 2
        self.dark_overlay = pygame.Surface((BOARD_WIDTH, BOARD_HEIGHT))
        self.update_brightness()

    def load_images(self):
        try:
            self.background_img = pygame.image.load("flappybirdbg.png").convert()
            self.bird_img = pygame.image.load("flappybird.png").convert_alpha()
            self.top_pipe_img = pygame.image.load("toppipe.png").convert_alpha()
            self.bottom_pipe_img = pygame.image.load("bottompipe.png").convert_alpha()
            self.coin_img = pygame.image.load("flappybirdcoin.png").convert_alpha()
        except:
            self.background_img = pygame.Surface((BOARD_WIDTH, BOARD_HEIGHT))
            self.background_img.fill((135, 206, 235))
            pygame.draw.ellipse(self.background_img, (255, 255, 255), (50, 50, 60, 40))
            self.bird_img = pygame.Surface((BIRD_WIDTH, BIRD_HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(self.bird_img, (255, 255, 0), (0, 0, BIRD_WIDTH, BIRD_HEIGHT))
            self.top_pipe_img = pygame.Surface((PIPE_WIDTH, PIPE_HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(self.top_pipe_img, (0, 128, 0), (0, 0, PIPE_WIDTH, PIPE_HEIGHT))
            self.bottom_pipe_img = pygame.Surface((PIPE_WIDTH, PIPE_HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(self.bottom_pipe_img, (0, 128, 0), (0, 0, PIPE_WIDTH, PIPE_HEIGHT))
            self.coin_img = pygame.Surface((COIN_WIDTH, COIN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(self.coin_img, (255, 223, 0), (COIN_WIDTH // 2, COIN_HEIGHT // 2), COIN_WIDTH // 2)
            pygame.draw.circle(self.coin_img, (255, 255, 0), (COIN_WIDTH // 2, COIN_HEIGHT // 2), COIN_WIDTH // 2, 3)
        self.background_img = pygame.transform.scale(self.background_img, (BOARD_WIDTH, BOARD_HEIGHT))
        self.bird_img = pygame.transform.scale(self.bird_img, (BIRD_WIDTH, BIRD_HEIGHT))
        self.top_pipe_img = pygame.transform.scale(self.top_pipe_img, (PIPE_WIDTH, PIPE_HEIGHT))
        self.bottom_pipe_img = pygame.transform.scale(self.bottom_pipe_img, (PIPE_WIDTH, PIPE_HEIGHT))
        self.coin_img = pygame.transform.scale(self.coin_img, (COIN_WIDTH, COIN_HEIGHT))

    def load_sounds(self):
        try:
            self.music = pygame.mixer.Sound("flappybirdmusic.mp3")
            self.crash_sound = pygame.mixer.Sound("flappybirdcrash.mp3")
            self.coin_sound = pygame.mixer.Sound("flappybirdcoinmusic.mp3")
            self.button_click_sound = pygame.mixer.Sound("flappybirdbuttonclicksound.mp3")
        except:
            self.music = pygame.mixer.Sound(buffer=bytearray(100))
            self.crash_sound = pygame.mixer.Sound(buffer=bytearray(100))
            self.coin_sound = pygame.mixer.Sound(buffer=bytearray(100))
            self.button_click_sound = pygame.mixer.Sound(buffer=bytearray(100))
        self.set_volume(self.volume)

    def set_volume(self, volume):
        self.volume = volume
        self.music.set_volume(volume)
        self.crash_sound.set_volume(volume)
        self.coin_sound.set_volume(volume)
        self.button_click_sound.set_volume(volume)

    def update_brightness(self):
        alpha = int(255 * (1 - self.brightness))
        self.dark_overlay.fill((0, 0, 0))
        self.dark_overlay.set_alpha(alpha)

    def reset(self):
        self.bird.y = self.bird_y
        self.velocity_y = 0
        self.pipes = []
        self.coins = []
        self.game_over = False
        self.score = 0
        self.last_pipe_time = pygame.time.get_ticks()
        self.difficulty_level = 0
        self.velocity_x = -4
        self.pipe_interval = 1500
        self.music_playing = True
        self.music.play(-1)

    def update_background(self):
        self.bg_x1 -= self.bg_speed
        self.bg_x2 -= self.bg_speed
        if self.bg_x1 <= -BOARD_WIDTH:
            self.bg_x1 = BOARD_WIDTH
        if self.bg_x2 <= -BOARD_WIDTH:
            self.bg_x2 = BOARD_WIDTH

    def place_pipes(self):
        opening_space = BOARD_HEIGHT // 4
        base_pipe_y = random.randint(-PIPE_HEIGHT + 100, -100)
        pipe_x = BOARD_WIDTH
        top_pipe_y = base_pipe_y + random.randint(-100, 100)
        move_pipe = random.random() < self.difficulty_level * 0.1
        top_pipe = Pipe(self.top_pipe_img, pipe_x, top_pipe_y, PIPE_WIDTH, PIPE_HEIGHT, move_pipe)
        bottom_pipe = Pipe(self.bottom_pipe_img, pipe_x,
                           top_pipe_y + PIPE_HEIGHT + opening_space,
                           PIPE_WIDTH, PIPE_HEIGHT, move_pipe)
        if random.random() < 0.3 + (self.difficulty_level * 0.05):
            coin_y = top_pipe_y + PIPE_HEIGHT + random.randint(20, opening_space - COIN_HEIGHT - 20)
            self.coins.append(Coin(self.coin_img, pipe_x + PIPE_WIDTH, coin_y, COIN_WIDTH, COIN_HEIGHT))
        self.pipes.append(top_pipe)
        self.pipes.append(bottom_pipe)

    def jump(self):
        if self.game_over:
            self.reset()
        self.velocity_y = -12

    def update_difficulty(self):
        thresholds = [0, 5, 10, 20, 30, 40, 50]
        for i, th in enumerate(thresholds):
            if self.score >= th:
                self.difficulty_level = i
        self.velocity_x = -4 - self.difficulty_level
        self.pipe_interval = max(600, 1500 - self.difficulty_level * 150)
        self.bg_speed = 2 + self.difficulty_level // 2

    def update(self):
        if self.game_over:
            return
        self.update_background()
        self.update_difficulty()
        self.velocity_y += self.gravity
        self.bird.y += self.velocity_y
        self.bird.y = max(0, self.bird.y)
        if self.bird.y + self.bird.height > BOARD_HEIGHT:
            self.handle_game_over()
        current_time = pygame.time.get_ticks()
        if current_time - self.last_pipe_time > self.pipe_interval:
            self.place_pipes()
            self.last_pipe_time = current_time
        for pipe in self.pipes[:]:
            pipe.x += self.velocity_x
            pipe.update()
            if not pipe.passed and self.bird.x > pipe.x + pipe.width:
                self.score += 0.5
                pipe.passed = True
            if self.check_collision(self.bird, pipe):
                self.handle_game_over()
            if pipe.x + pipe.width < 0:
                self.pipes.remove(pipe)
        for coin in self.coins[:]:
            coin.x += self.velocity_x
            coin.rotation = (coin.rotation + coin.rotation_speed) % 360
            if self.check_collision(self.bird, coin):
                self.score += 2
                self.coin_sound.play()
                self.coins.remove(coin)
            if coin.x + coin.width < 0:
                self.coins.remove(coin)

    def handle_game_over(self):
        self.game_over = True
        self.music.stop()
        self.music_playing = False
        self.crash_sound.play()

    def check_collision(self, obj1, obj2):
        return (obj1.x < obj2.x + obj2.width and
                obj1.x + obj1.width > obj2.x and
                obj1.y < obj2.y + obj2.height and
                obj1.y + obj1.height > obj2.y)

    def draw(self):
        self.screen.blit(self.background_img, (self.bg_x1, 0))
        self.screen.blit(self.background_img, (self.bg_x2, 0))
        for pipe in self.pipes:
            self.screen.blit(pipe.img, (pipe.x, pipe.y))
        for coin in self.coins:
            rotated_image = pygame.transform.rotate(coin.img, coin.rotation)
            rect = rotated_image.get_rect(center=(coin.x + coin.width // 2, coin.y + coin.height // 2))
            self.screen.blit(rotated_image, rect.topleft)
        self.screen.blit(self.bird.img, (self.bird.x, self.bird.y))
        if self.brightness < 1.0:
            self.screen.blit(self.dark_overlay, (0, 0))
        score_text = f"Score: {int(self.score)}"
        score_surface = FONT.render(score_text, True, (255, 255, 255))
        self.screen.blit(score_surface, (10, 10))
        info_text = "ESC = Pause"
        info_surface = SMALL_FONT.render(info_text, True, (255, 255, 255))
        self.screen.blit(info_surface, (BOARD_WIDTH - 200, 10))


def draw_text_center(screen, text, font, color, y, offset=0):
    text_surface = font.render(text, True, color)
    rect = text_surface.get_rect(center=(BOARD_WIDTH // 2, y + offset))
    screen.blit(text_surface, rect)


def draw_credits(screen):
    credit_lines = [
        "Developer: Soleman Hossain",
        "Contact: muzankibu977@gmail.com",
        "",
        "Copyright (c) 2025 Soleman Hossain",
        "All rights reserved. This game and its source code are the property of Soleman Hossain.",
    ]
    y_pos = BOARD_HEIGHT - 150
    for line in credit_lines:
        if line:
            text_surface = TINY_FONT.render(line, True, (200, 200, 200))
            text_rect = text_surface.get_rect(center=(BOARD_WIDTH // 2, y_pos))
            screen.blit(text_surface, text_rect)
        y_pos += 15


def button(screen, msg, x, y, w, h, inactive_color, active_color, action=None, game=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        pygame.draw.rect(screen, active_color, (x, y, w, h))
        if click[0] == 1 and action is not None:
            if game:
                game.button_click_sound.play()
            action()
    else:
        pygame.draw.rect(screen, inactive_color, (x, y, w, h))
    text_surface = SMALL_FONT.render(msg, True, (0, 0, 0))
    text_rect = text_surface.get_rect(center=(x + w // 2, y + h // 2))
    screen.blit(text_surface, text_rect)


def main():
    screen = pygame.display.set_mode((BOARD_WIDTH, BOARD_HEIGHT))
    pygame.display.set_caption("Flappy Bird: Dark Continent")
    clock = pygame.time.Clock()
    game = FlappyBirdGame(screen)
    state = MAIN_MENU
    user_name = ""
    input_text = ""
    high_scores = load_high_scores()
    volume_slider = Slider(BOARD_WIDTH // 2 - 100, BOARD_HEIGHT // 3 + 50, 200, 10, 0, 1, game.volume)
    brightness_slider = Slider(BOARD_WIDTH // 2 - 100, BOARD_HEIGHT // 2 + 50, 200, 10, 0.1, 1, game.brightness)
    try:
        menu_bg = pygame.image.load("flappybirdmenubg.png").convert()
        menu_bg = pygame.transform.scale(menu_bg, (BOARD_WIDTH, BOARD_HEIGHT))
    except:
        menu_bg = pygame.Surface((BOARD_WIDTH, BOARD_HEIGHT))
        menu_bg.fill((0, 0, 0))

    title_offset = 0
    title_time = 0

    def start_new_game():
        nonlocal state, user_name, input_text
        input_text = ""
        state = GET_USERNAME

    def quit_game():
        pygame.quit()
        sys.exit()

    def show_high_scores():
        nonlocal state
        game.button_click_sound.play()
        state = HIGH_SCORES
        game.music.stop()

    def show_settings():
        nonlocal state
        game.button_click_sound.play()
        state = SETTINGS
        game.music.stop()

    def back_to_menu():
        nonlocal state
        game.button_click_sound.play()
        state = MAIN_MENU
        game.music.stop()

    def resume_game():
        nonlocal state
        game.button_click_sound.play()
        state = PLAYING
        pygame.mixer.unpause()
        game.music_playing = True

    def cycle_control_scheme():
        game.button_click_sound.play()
        schemes = ["space", "mouse", "up_arrow"]
        current_index = schemes.index(game.control_scheme)
        game.control_scheme = schemes[(current_index + 1) % len(schemes)]

    def show_instructions():
        nonlocal state
        game.button_click_sound.play()
        state = INSTRUCTIONS
        game.music.stop()

    running = True
    while running:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if state == GET_USERNAME:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    elif event.key == pygame.K_RETURN:
                        if input_text.strip() != "":
                            user_name = input_text.strip()
                            game.user_name = user_name
                            game.reset()
                            state = PLAYING
                    else:
                        if len(input_text) < 15:
                            input_text += event.unicode
            elif state == PLAYING:
                if event.type == pygame.KEYDOWN:
                    if (event.key == pygame.K_SPACE and game.control_scheme == "space") or \
                       (event.key == pygame.K_UP and game.control_scheme == "up_arrow"):
                        game.jump()
                    elif event.key == pygame.K_ESCAPE:
                        state = PAUSED
                        pygame.mixer.pause()
                        game.music_playing = False
                elif event.type == pygame.MOUSEBUTTONDOWN and game.control_scheme == "mouse":
                    game.jump()
            elif state == PAUSED:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        resume_game()
            elif state == GAME_OVER:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        high_scores = update_high_scores(game.user_name, int(game.score), high_scores)
                        save_high_scores(high_scores)
                        state = MAIN_MENU
            elif state == SETTINGS:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        back_to_menu()
                if volume_slider.handle_event(event):
                    game.set_volume(volume_slider.val)
                if brightness_slider.handle_event(event):
                    game.brightness = brightness_slider.val
                    game.update_brightness()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    control_button_rect = pygame.Rect(BOARD_WIDTH // 2 - 150, BOARD_HEIGHT // 2 + 120, 300, 50)
                    if control_button_rect.collidepoint(mouse_pos):
                        cycle_control_scheme()
            elif state == INSTRUCTIONS:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        back_to_menu()

        title_time += 0.05
        title_offset = math.sin(title_time) * 5

        if state == MAIN_MENU:
            screen.blit(menu_bg, (0, 0))
            draw_text_center(screen, "Flappy Bird: Dark Continent", TITLE_FONT, (0, 100, 0), BOARD_HEIGHT // 4,
                             title_offset)
            button(screen, "Start New Game", BOARD_WIDTH // 2 - 150, BOARD_HEIGHT // 2 - 80, 300, 50,
                   (100, 255, 100), (50, 200, 50), start_new_game, game)
            button(screen, "High Scores", BOARD_WIDTH // 2 - 150, BOARD_HEIGHT // 2 - 10, 300, 50,
                   (100, 100, 255), (50, 50, 200), show_high_scores, game)
            button(screen, "Settings", BOARD_WIDTH // 2 - 150, BOARD_HEIGHT // 2 + 60, 300, 50,
                   (255, 255, 100), (200, 200, 50), show_settings, game)
            button(screen, "Game Instructions", BOARD_WIDTH // 2 - 150, BOARD_HEIGHT // 2 + 130, 300, 50,
                   (255, 165, 0), (200, 120, 0), show_instructions, game)
            button(screen, "Quit", BOARD_WIDTH // 2 - 150, BOARD_HEIGHT // 2 + 200, 300, 50,
                   (255, 100, 100), (200, 50, 50), quit_game, game)
            draw_credits(screen)

        elif state == INSTRUCTIONS:
            screen.blit(menu_bg, (0, 0))
            instructions = [
                "Listen Carefully!",
                "",
                "1. Tap space to fly or R.I.P!",
                "2. Grab coins, be a spooky score thief!",
                "3. Dodge pipes, ground, and sky—it's ALL evil!",
                "4. ESC to pause, resume, or flee like a scared specter!",
                "",
                "Good luck... you'll need it!"
            ]
            y = BOARD_HEIGHT // 6
            for line in instructions:
                draw_text_center(screen, line, FONT if line.startswith("Listen") else SMALL_FONT,
                                 (255, 255, 255), y)
                y += 40
            button(screen, "Back to Main Menu", BOARD_WIDTH // 2 - 150, BOARD_HEIGHT - 150, 300, 50,
                   (255, 100, 100), (200, 50, 50), back_to_menu, game)

        elif state == GET_USERNAME:
            draw_text_center(screen, "HAHAHA! There is no going back now!", FONT, (56, 0, 0), BOARD_HEIGHT // 3)
            pygame.draw.rect(screen, (255, 255, 255), (BOARD_WIDTH // 2 - 200, BOARD_HEIGHT // 2 - 25, 400, 50), 2)
            input_surface = FONT.render(input_text, True, (255, 255, 255))
            screen.blit(input_surface, (BOARD_WIDTH // 2 - 190, BOARD_HEIGHT // 2 - 20))
            draw_text_center(screen, "Type your name and enter to start", SMALL_FONT, (200, 200, 200), BOARD_HEIGHT // 2 + 50)
        elif state == PLAYING:
            game.update()
            game.draw()
            if game.game_over:
                state = GAME_OVER
        elif state == PAUSED:
            game.draw()
            draw_text_center(screen, "Paused", FONT, (255, 255, 0), BOARD_HEIGHT // 3)
            draw_text_center(screen, f"Your Score: {int(game.score)}", FONT, (255, 255, 255), BOARD_HEIGHT // 3 + 50)
            button(screen, "Resume", BOARD_WIDTH // 2 - 150, BOARD_HEIGHT // 2 + 100, 300, 50,
                   (100, 255, 100), (50, 200, 50), resume_game, game)
            button(screen, "Return to Main Menu", BOARD_WIDTH // 2 - 150, BOARD_HEIGHT // 2 + 170, 300, 50,
                   (255, 100, 100), (200, 50, 50), back_to_menu, game)
        elif state == GAME_OVER:
            game.draw()
            draw_text_center(screen, "Game Over!", FONT, (255, 0, 0), BOARD_HEIGHT // 3)
            draw_text_center(screen, f"Your Score: {int(game.score)}", FONT, (255, 255, 255), BOARD_HEIGHT // 3 + 50)
            draw_text_center(screen, "Press Enter to return to menu", SMALL_FONT, (200, 200, 200), BOARD_HEIGHT // 2)
        elif state == HIGH_SCORES:
            draw_text_center(screen, "High Scores", FONT, (255, 255, 255), BOARD_HEIGHT // 6)
            for idx, entry in enumerate(high_scores):
                score_text = f"{idx + 1}. {entry['name']} - {entry['score']}"
                screen.blit(FONT.render(score_text, True, (255, 255, 255)),
                            (BOARD_WIDTH // 3, BOARD_HEIGHT // 4 + idx * 40))
            button(screen, "Back to Menu", BOARD_WIDTH // 2 - 150, BOARD_HEIGHT - 150, 300, 50,
                   (255, 100, 100), (200, 50, 50), back_to_menu, game)
        elif state == SETTINGS:
            screen.blit(menu_bg, (0, 0))
            draw_text_center(screen, "Settings", FONT, (255, 255, 255), BOARD_HEIGHT // 6)
            draw_text_center(screen, "Volume", SMALL_FONT, (255, 255, 255), BOARD_HEIGHT // 3 - 20)
            volume_slider.draw(screen)
            draw_text_center(screen, f"{int(volume_slider.val * 100)}%", SMALL_FONT, (255, 255, 255),
                             BOARD_HEIGHT // 3 + 20)
            draw_text_center(screen, "Brightness", SMALL_FONT, (255, 255, 255), BOARD_HEIGHT // 2 - 20)
            brightness_slider.draw(screen)
            draw_text_center(screen, f"{int(brightness_slider.val * 100)}%", SMALL_FONT, (255, 255, 255),
                             BOARD_HEIGHT // 2 + 20)
            button(screen, f"Controls: {game.control_scheme.replace('_', ' ').title()}",
                   BOARD_WIDTH // 2 - 150, BOARD_HEIGHT // 2 + 120, 300, 50,
                   (200, 200, 200), (150, 150, 150), cycle_control_scheme, game)
            button(screen, "Back to Menu", BOARD_WIDTH // 2 - 150, BOARD_HEIGHT - 150, 300, 50,
                   (255, 100, 100), (200, 50, 50), back_to_menu, game)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()