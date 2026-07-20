import pygame
import sys
import random
import array

pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=1)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("2D Subway Runner - Enhanced Edition")
clock = pygame.time.Clock()
FPS = 60

SOFT_PINK = (250, 218, 221)
CREAM = (255, 247, 245)
LIGHT_BEIGE = (242, 233, 228)
BLACK = (40, 40, 40)
WHITE = (255, 255, 255)
GOLD = (255, 215, 0)
OBSTACLE_RED = (235, 87, 87)
GROUND_GRAY = (180, 180, 180)
BUTTON_COLOR = (120, 200, 160)
BUTTON_HOVER = (90, 180, 130)

font_title = pygame.font.SysFont("arial", 28, bold=True)
font_medium = pygame.font.SysFont("arial", 20, bold=True)
font_small = pygame.font.SysFont("arial", 15)

def create_tone(frequency, duration, volume=0.25):
    sample_rate = 22050
    n_samples = int(sample_rate * duration)
    buf = array.array('h', [0] * n_samples)
    for i in range(n_samples):
        t = float(i) / sample_rate
        val = int(volume * 32767.0 * (1 if (int(t * frequency * 2) % 2) == 0 else -1))
        buf[i] = val
    return pygame.mixer.Sound(buf)

SND_JUMP = create_tone(523, 0.1)
SND_COIN = create_tone(880, 0.12)
SND_GAMEOVER = create_tone(150, 0.4)

CHARACTERS = [
    {
        "name": "Cubey",
        "type": "geometry",
        "shape": "square",
        "color": (255, 120, 150),
        "jump_power": -14,
        "desc": "Balanced Square"
    },
    {
        "name": "Orbita",
        "type": "geometry",
        "shape": "circle",
        "color": (100, 200, 250),
        "jump_power": -16,
        "desc": "High Jump Circle"
    },
    {
        "name": "Hexa",
        "type": "geometry",
        "shape": "diamond",
        "color": (180, 130, 240),
        "jump_power": -15,
        "desc": "Agile Diamond"
    },
    {
        "name": "Starry",
        "type": "avatar",
        "badge": "star",
        "color": (255, 180, 50),
        "jump_power": -13,
        "desc": "Star Badge Runner"
    },
    {
        "name": "Pinkie",
        "type": "geometry",
        "shape": "square",
        "color": (255, 182, 193),
        "jump_power": -14,
        "desc": "Soft Pink Runner"
    },
    {
        "name": "Royalty",
        "type": "avatar",
        "badge": "crown",
        "color": (150, 220, 200),
        "jump_power": -15,
        "desc": "Crown Badge Avatar"
    }
]

GROUND_Y = 320

def draw_button(text, rect, is_hovered):
    color = BUTTON_HOVER if is_hovered else BUTTON_COLOR
    pygame.draw.rect(screen, color, rect, border_radius=10)
    pygame.draw.rect(screen, BLACK, rect, 2, border_radius=10)
    btn_text = font_medium.render(text, True, BLACK)
    screen.blit(btn_text, btn_text.get_rect(center=rect.center))

class Runner:
    def __init__(self, char_data):
        self.char = char_data
        self.normal_height = 50
        self.duck_height = 25
        self.width = 35
        
        self.rect = pygame.Rect(100, GROUND_Y - self.normal_height, self.width, self.normal_height)
        self.vel_y = 0
        self.is_jumping = False
        self.is_ducking = False

    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and not self.is_jumping:
            self.vel_y = self.char["jump_power"]
            self.is_jumping = True
            SND_JUMP.play()

        if keys[pygame.K_DOWN] and not self.is_jumping:
            if not self.is_ducking:
                self.is_ducking = True
                self.rect.height = self.duck_height
                self.rect.y = GROUND_Y - self.duck_height
        else:
            if self.is_ducking:
                self.is_ducking = False
                self.rect.height = self.normal_height
                self.rect.y = GROUND_Y - self.normal_height

    def update(self):
        self.vel_y += 0.8
        self.rect.y += self.vel_y

        current_h = self.duck_height if self.is_ducking else self.normal_height
        if self.rect.y >= GROUND_Y - current_h:
            self.rect.y = GROUND_Y - current_h
            self.vel_y = 0
            self.is_jumping = False

    def draw(self, override_pos=None):
        draw_rect = self.rect if override_pos is None else pygame.Rect(override_pos[0], override_pos[1], self.width, self.rect.height)
        x, y = draw_rect.x, draw_rect.y
        color = self.char["color"]

        if self.char["type"] == "geometry":
            if self.char["shape"] == "square":
                pygame.draw.rect(screen, color, draw_rect, border_radius=6)
                pygame.draw.rect(screen, BLACK, draw_rect, 2, border_radius=6)
            elif self.char["shape"] == "circle":
                pygame.draw.ellipse(screen, color, draw_rect)
                pygame.draw.ellipse(screen, BLACK, draw_rect, 2)
            elif self.char["shape"] == "diamond":
                pts = [(x + 17, y), (x + 35, y + 25), (x + 17, y + 50), (x, y + 25)]
                pygame.draw.polygon(screen, color, pts)
                pygame.draw.polygon(screen, BLACK, pts, 2)

            if not self.is_ducking:
                pygame.draw.circle(screen, BLACK, (x + 24, y + 15), 2)
                pygame.draw.arc(screen, BLACK, (x + 18, y + 20, 10, 8), 3.14, 0, 2)

        elif self.char["type"] == "avatar":
            pygame.draw.rect(screen, color, draw_rect, border_radius=8)
            pygame.draw.rect(screen, BLACK, draw_rect, 2, border_radius=8)
            cx, cy = draw_rect.center
            if self.char.get("badge") == "crown":
                pygame.draw.polygon(screen, GOLD, [(cx - 8, cy + 4), (cx - 8, cy - 6), (cx - 4, cy - 2), (cx, cy - 8), (cx + 4, cy - 2), (cx + 8, cy - 6), (cx + 8, cy + 4)])
            else:
                pygame.draw.circle(screen, GOLD, (cx, cy), 6)


class Obstacle:
    def __init__(self, speed, obs_type):
        self.obs_type = obs_type
        if self.obs_type == "low":
            self.rect = pygame.Rect(SCREEN_WIDTH, GROUND_Y - 40, 30, 40)
        else:
            self.rect = pygame.Rect(SCREEN_WIDTH, GROUND_Y - 80, 40, 45)
        self.speed = speed

    def update(self):
        self.rect.x -= self.speed

    def draw(self):
        pygame.draw.rect(screen, OBSTACLE_RED, self.rect, border_radius=4)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=4)


class Coin:
    def __init__(self, speed, height_type):
        y_pos = GROUND_Y - 30 if height_type == "low" else GROUND_Y - 75
        self.rect = pygame.Rect(SCREEN_WIDTH, y_pos, 16, 16)
        self.speed = speed

    def update(self):
        self.rect.x -= self.speed

    def draw(self):
        pygame.draw.circle(screen, GOLD, self.rect.center, 8)
        pygame.draw.circle(screen, BLACK, self.rect.center, 8, 1)


def select_character():
    index = 0
    start_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 80, 320, 160, 45)

    card_rect = pygame.Rect(SCREEN_WIDTH // 2 - 140, 80, 280, 220)
    
    left_arrow_rect = pygame.Rect(card_rect.left - 45, card_rect.centery - 25, 35, 50)
    right_arrow_rect = pygame.Rect(card_rect.right + 10, card_rect.centery - 25, 35, 50)

    while True:
        clock.tick(FPS)
        screen.fill(CREAM)
        mouse_pos = pygame.mouse.get_pos()

        t_surf = font_title.render("SELECT RUNNER", True, BLACK)
        screen.blit(t_surf, t_surf.get_rect(center=(SCREEN_WIDTH // 2, 40)))

        char = CHARACTERS[index]
        pygame.draw.rect(screen, SOFT_PINK, card_rect, border_radius=15)
        pygame.draw.rect(screen, BLACK, card_rect, 3, border_radius=15)

        dummy = Runner(char)
        dummy.draw(override_pos=(SCREEN_WIDTH // 2 - 17, 120))

        n_surf = font_title.render(char["name"], True, BLACK)
        screen.blit(n_surf, n_surf.get_rect(center=(SCREEN_WIDTH // 2, 195)))

        d_surf = font_small.render(char["desc"], True, BLACK)
        screen.blit(d_surf, d_surf.get_rect(center=(SCREEN_WIDTH // 2, 225)))

        hint_surf = font_small.render("< Use Arrows or Click Fleches >", True, BLACK)
        screen.blit(hint_surf, hint_surf.get_rect(center=(SCREEN_WIDTH // 2, 260)))

        left_hover = left_arrow_rect.collidepoint(mouse_pos)
        right_hover = right_arrow_rect.collidepoint(mouse_pos)

        draw_button("<", left_arrow_rect, left_hover)
        draw_button(">", right_arrow_rect, right_hover)

        start_hover = start_btn_rect.collidepoint(mouse_pos)
        draw_button("START GAME", start_btn_rect, start_hover)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    index = (index - 1) % len(CHARACTERS)
                elif event.key == pygame.K_RIGHT:
                    index = (index + 1) % len(CHARACTERS)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return CHARACTERS[index]

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if left_hover:
                    index = (index - 1) % len(CHARACTERS)
                elif right_hover:
                    index = (index + 1) % len(CHARACTERS)
                elif start_hover:
                    return CHARACTERS[index]


def show_game_over(score, high_score):
    replay_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 80, 230, 160, 45)

    while True:
        clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()

        overlay = pygame.Surface((360, 220))
        overlay.fill(LIGHT_BEIGE)
        overlay_rect = overlay.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(overlay, overlay_rect)
        pygame.draw.rect(screen, BLACK, overlay_rect, 3, border_radius=12)

        go_surf = font_title.render("GAME OVER", True, OBSTACLE_RED)
        screen.blit(go_surf, go_surf.get_rect(center=(SCREEN_WIDTH // 2, 130)))

        sc_surf = font_medium.render(f"Score: {score}  |  High: {high_score}", True, BLACK)
        screen.blit(sc_surf, sc_surf.get_rect(center=(SCREEN_WIDTH // 2, 175)))

        is_hovered = replay_btn_rect.collidepoint(mouse_pos)
        draw_button("REPLAY", replay_btn_rect, is_hovered)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if is_hovered:
                    return


def main():
    high_score = 0

    while True:
        chosen_char = select_character()
        player = Runner(chosen_char)

        obstacles = []
        coins = []
        game_speed = 6
        score = 0
        collected_coins = 0
        spawn_timer = 0
        game_over = False

        while not game_over:
            clock.tick(FPS)
            spawn_timer += 1
            score += 1

            if score % 500 == 0:
                game_speed += 0.5

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            player.handle_input()
            player.update()

            if spawn_timer > random.randint(60, 95):
                spawn_timer = 0
                obs_type = random.choice(["low", "high"])
                obstacles.append(Obstacle(game_speed, obs_type))
                
                if random.random() < 0.5:
                    coin_height = "high" if obs_type == "low" else "low"
                    coins.append(Coin(game_speed, coin_height))

            for obs in obstacles[:]:
                obs.update()
                if obs.rect.right < 0:
                    obstacles.remove(obs)
                if player.rect.colliderect(obs.rect):
                    SND_GAMEOVER.play()
                    game_over = True
                    if score > high_score:
                        high_score = score

            for coin in coins[:]:
                coin.update()
                if coin.rect.right < 0:
                    coins.remove(coin)
                elif player.rect.colliderect(coin.rect):
                    coins.remove(coin)
                    collected_coins += 1
                    score += 100
                    SND_COIN.play()

            screen.fill(LIGHT_BEIGE)

            pygame.draw.rect(screen, GROUND_GRAY, (0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y))
            pygame.draw.line(screen, BLACK, (0, GROUND_Y), (SCREEN_WIDTH, GROUND_Y), 3)

            for obs in obstacles:
                obs.draw()
            for coin in coins:
                coin.draw()

            player.draw()

            s_text = font_medium.render(f"Score: {score}", True, BLACK)
            hs_text = font_small.render(f"High Score: {high_score}", True, BLACK)
            c_text = font_medium.render(f"Coins: {collected_coins}", True, GOLD)

            screen.blit(s_text, (20, 15))
            screen.blit(hs_text, (20, 40))
            screen.blit(c_text, (SCREEN_WIDTH - 120, 15))

            pygame.display.update()

        show_game_over(score, high_score)


if __name__ == "__main__":
    main()