import pygame
from sys import exit
import random
import json   # [BARU]
import math   # [BARU]
import os     # [BARU]

# game variables
GAME_WIDTH = 360
GAME_HEIGHT = 640

bird_x = GAME_WIDTH / 8
bird_y = GAME_HEIGHT / 2
brid_width = 34
bird_height = 24

class Bird(pygame.Rect):
    def __init__(self, img):
        pygame.Rect.__init__(self, bird_x, bird_y, brid_width, bird_height)
        self.image = img

#pipes class
pipe_x = GAME_WIDTH
pipe_y = 0
pipe_width = 64
pipe_height = 512

class Pipe(pygame.Rect):
    def __init__(self, img, counts_for_score=False):
        pygame.Rect.__init__(self, pipe_x, pipe_y, pipe_width, pipe_height)
        self.image = img
        self.passed = False
        self.counts_for_score = counts_for_score

#Game images 
background_imaege = pygame.image.load("flappybirdbg.png")
bird_image = pygame.image.load("flappybird.png")
bird_image = pygame.transform.scale(bird_image, (brid_width, bird_height))
top_pipe_image = pygame.image.load("toppipe.png")
top_pipe_image = pygame.transform.scale(top_pipe_image, (pipe_width, pipe_height))
bottom_pipe_image = pygame.image.load("bottompipe.png")
bottom_pipe_image = pygame.transform.scale(bottom_pipe_image, (pipe_width, pipe_height))

#Game logic
bird = Bird(bird_image)
pipes = []
velocity_x = -2
velocity_y = 0
gravity = 0.4
score = 0
game_over = False

def draw():
    window.blit(background_imaege, (0, 0))
    window.blit(bird.image, bird)

    for pipe in pipes:
        window.blit(pipe.image, pipe)

    text_str = str(int(score))
    # [UBAH] tulisan "Game Over: ..." dan "Press Space to restart" dipindah ke
    # layar game over yang baru (draw_game_over), jadi dihapus dari sini.

    text_font = pygame.font.Font(None, 45)
    text_render = text_font.render(text_str, True, "white")
    window.blit(text_render, (5, 0))

def move():
    global velocity_y, score, game_over 
    velocity_y += gravity
    bird.y += velocity_y
    bird.y = max(bird.y, 0)

    if bird.y > GAME_HEIGHT:
        game_over = True
        return

    for pipe in pipes:
        pipe.x += velocity_x

        if pipe.counts_for_score and not pipe.passed and bird.x > pipe.x + pipe.width:
            score += 1
            pipe.passed = True

        if bird.colliderect(pipe):
            game_over = True
            return

    while len(pipes) > 0 and pipes[0].x + pipes[0].width < 0:
        pipes.pop(0)

def create_pipe():
    random_pipe_y = pipe_y - pipe_height/4 - random.random() * (pipe_height/2)
    opening_space = GAME_HEIGHT / 4


    top_pipe = Pipe(top_pipe_image, counts_for_score=True)
    top_pipe.y = random_pipe_y
    pipes.append(top_pipe)

    bottom_pipe = Pipe(bottom_pipe_image)
    bottom_pipe.y = top_pipe.y + top_pipe.height + opening_space
    pipes.append(bottom_pipe)

def restart_game():
    global bird, velocity_y, score, game_over
    bird = Bird(bird_image)
    pipes.clear()
    velocity_y = 0
    score = 0
    game_over = False

pygame.init()
window = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
pygame.display.set_caption("Flappy Bird")
Clock = pygame.time.Clock()

create_pipes_timer = pygame.USEREVENT + 0
pygame.time.set_timer(create_pipes_timer, 1500)


# =====================================================================
# [BARU] MAIN MENU, GET READY, DAN GAME OVER
# Alur: menu -> ready -> playing -> gameover -> (OK = menu / PLAY = ready)
# =====================================================================
INK = (84, 56, 71)
WHITE = (255, 255, 255)
ORANGE = (232, 97, 1)
GREEN = (115, 191, 46)
SAND = (222, 216, 149)
TITLE_COLOR = (248, 163, 14)
SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "highscore.json")

def load_best():
    try:
        with open(SAVE_FILE) as f:
            return int(json.load(f).get("best", 0))
    except (OSError, ValueError):
        return 0

def save_best(value):
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump({"best": value}, f)
    except OSError:
        pass

title_font = pygame.font.Font(None, 84)
title_font.set_bold(True)
msg_font = pygame.font.Font(None, 62)
msg_font.set_bold(True)
num_font = pygame.font.Font(None, 48)
label_font = pygame.font.Font(None, 28)
btn_font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

big_bird = pygame.transform.scale(bird_image, (brid_width * 2, bird_height * 2))

def outlined_text(text, fnt, color, pos, anchor="center", thick=2, shadow=2, outline=INK):
    """Teks dengan outline gelap + bayangan bawah (mirip tulisan di game aslinya)."""
    dark = fnt.render(text, True, outline)
    light = fnt.render(text, True, color)
    r = light.get_rect(**{anchor: pos})
    for dx in range(-thick, thick + 1):
        for dy in range(-thick, thick + shadow + 1):
            window.blit(dark, (r.x + dx, r.y + dy))
    window.blit(light, r)

class Button:
    def __init__(self, label, center, color, width=120, height=46):
        self.label, self.color = label, color
        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.center = center
        self.down = False

    def draw(self):
        r = self.rect.move(0, 3 if self.down else 0)
        pygame.draw.rect(window, INK, r.inflate(8, 8))
        pygame.draw.rect(window, WHITE, r.inflate(4, 4))
        pygame.draw.rect(window, self.color, r)
        dark = tuple(max(c - 60, 0) for c in self.color)
        light = tuple(min(c + 50, 255) for c in self.color)
        pygame.draw.rect(window, dark, (r.x, r.bottom - 6, r.w, 6))
        pygame.draw.rect(window, light, (r.x, r.y, r.w, 3))
        outlined_text(self.label, btn_font, WHITE, r.center, thick=1, shadow=1)

    def handle(self, e):
        """True kalau tombol diklik (tekan + lepas di atas tombol)."""
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and self.rect.collidepoint(e.pos):
            self.down = True
        elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            hit = self.down and self.rect.collidepoint(e.pos)
            self.down = False
            return hit
        return False

start_btn = Button("START", (GAME_WIDTH // 2 - 75, 400), GREEN)
score_btn = Button("SCORE", (GAME_WIDTH // 2 + 75, 400), ORANGE)
ok_btn = Button("OK", (GAME_WIDTH // 2 - 75, 500), ORANGE)
play_btn = Button("PLAY", (GAME_WIDTH // 2 + 75, 500), GREEN)
back_btn = Button("OK", (GAME_WIDTH // 2, 500), ORANGE)

state = "menu"          # menu | ready | playing | gameover | score
best_score = load_best()
last_score = 0
new_best = False
flash = 0.0             # kilatan putih saat mati
panel_t = 0.0           # timer animasi layar game over

def medal_color(s):
    if s >= 40: return (225, 232, 235)   # platinum
    if s >= 30: return (255, 205, 40)    # emas
    if s >= 20: return (200, 204, 210)   # perak
    if s >= 10: return (205, 127, 50)    # perunggu
    return None

def draw_panel(center_y, shown_score, shown_best, is_new):
    panel = pygame.Rect(0, 0, 290, 150)
    panel.center = (GAME_WIDTH // 2, center_y)
    pygame.draw.rect(window, WHITE, panel.inflate(10, 10))
    pygame.draw.rect(window, INK, panel.inflate(6, 6))
    pygame.draw.rect(window, SAND, panel.inflate(-2, -2))
    pygame.draw.rect(window, (210, 176, 76), (panel.x + 1, panel.bottom - 6, panel.w - 2, 5))

    # medali (kiri)
    mx, my = panel.x + 60, panel.y + 88
    outlined_text("MEDAL", label_font, ORANGE, (mx, panel.y + 28), thick=1, shadow=0, outline=WHITE)
    col = medal_color(shown_score)
    pygame.draw.circle(window, INK, (mx, my), 31)
    if col:
        pygame.draw.circle(window, col, (mx, my), 28)
        pygame.draw.circle(window, tuple(max(c - 45, 0) for c in col), (mx, my), 20)
        pygame.draw.circle(window, col, (mx, my), 17)
    else:
        pygame.draw.circle(window, (170, 150, 90), (mx, my), 28)

    # skor (kanan)
    rx = panel.right - 22
    outlined_text("SCORE", label_font, ORANGE, (rx, panel.y + 24), "midright", thick=1, shadow=0, outline=WHITE)
    outlined_text(str(shown_score), num_font, WHITE, (rx, panel.y + 52), "midright", thick=2, shadow=1)
    outlined_text("BEST", label_font, ORANGE, (rx, panel.y + 90), "midright", thick=1, shadow=0, outline=WHITE)
    outlined_text(str(shown_best), num_font, WHITE, (rx, panel.y + 118), "midright", thick=2, shadow=1)
    if is_new:
        tag = pygame.Rect(0, 0, 44, 20)
        tag.midright = (rx - 62, panel.y + 90)
        pygame.draw.rect(window, INK, tag.inflate(4, 4))
        pygame.draw.rect(window, (232, 60, 40), tag)
        window.blit(small_font.render("NEW", True, WHITE), small_font.render("NEW", True, WHITE).get_rect(center=tag.center))

def draw_menu(t):
    window.blit(background_imaege, (0, 0))
    outlined_text("Flappy Bird", title_font, TITLE_COLOR, (GAME_WIDTH // 2, 130), thick=4, shadow=4)
    by = 262 + math.sin(t * 5) * 7
    window.blit(big_bird, big_bird.get_rect(center=(GAME_WIDTH // 2, by)))
    start_btn.draw()
    score_btn.draw()
    outlined_text("Space / klik untuk main", small_font, WHITE, (GAME_WIDTH // 2, 470), thick=1, shadow=1)

def draw_ready(t):
    window.blit(background_imaege, (0, 0))
    outlined_text("Get Ready!", msg_font, (252, 160, 70), (GAME_WIDTH // 2, 150), thick=3, shadow=3)
    window.blit(bird.image, (bird.x, bird.y + math.sin(t * 5) * 6))
    r = 16 + int(abs(math.sin(t * 4)) * 4)
    cx, cy = GAME_WIDTH // 2, 400
    pygame.draw.circle(window, INK, (cx, cy), r + 3)
    pygame.draw.circle(window, WHITE, (cx, cy), r)
    outlined_text("TAP", label_font, WHITE, (cx, cy + 46), thick=1, shadow=1)

def draw_game_over():
    k = min(panel_t / 0.5, 1.0)
    ease = 1 - (1 - k) ** 3
    outlined_text("Game Over", msg_font, (252, 160, 70),
                  (GAME_WIDTH // 2, 120 + ease * 60), thick=3, shadow=3)
    draw_panel(int(GAME_HEIGHT + 100 - ease * (GAME_HEIGHT + 100 - 330)), last_score, best_score, new_best)
    if panel_t > 0.7:
        ok_btn.draw()
        play_btn.draw()

def draw_flash():
    if flash > 0:
        overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        overlay.fill(WHITE)
        overlay.set_alpha(int(255 * flash))
        window.blit(overlay, (0, 0))

def go_ready():
    global state
    restart_game()
    state = "ready"

def start_playing():
    global state, velocity_y
    state = "playing"
    velocity_y = -6
    pygame.time.set_timer(create_pipes_timer, 1500)   # pipa pertama muncul 1,5 detik setelah tap

def on_death():
    global state, best_score, new_best, last_score, flash, panel_t
    last_score = int(score)
    new_best = last_score > best_score
    if new_best:
        best_score = last_score
        save_best(best_score)
    flash = 1.0
    panel_t = 0.0
    state = "gameover"


t = 0.0
dt = 0.0
while True: #Game loop
    t += dt
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == create_pipes_timer and state == "playing" and not game_over:
            create_pipe()

        key_tap = event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_RETURN)
        mouse_tap = (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                     and state in ("ready", "playing"))
        tap = key_tap or mouse_tap

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and state != "playing":
            state = "menu"

        if state == "menu":
            hit_start = start_btn.handle(event)
            hit_score = score_btn.handle(event)
            if hit_start or key_tap:
                go_ready()
            elif hit_score:
                state = "score"
        elif state == "ready":
            if tap:
                start_playing()
        elif state == "playing":
            if tap and not game_over:
                velocity_y = -6
        elif state == "gameover":
            if panel_t > 0.7:
                hit_ok = ok_btn.handle(event)
                hit_play = play_btn.handle(event)
                if hit_ok:
                    state = "menu"
                elif hit_play or key_tap:
                    go_ready()
        elif state == "score":
            if back_btn.handle(event) or key_tap:
                state = "menu"

    # ---- update ----
    if state == "playing":
        if not game_over:
            move()
        if game_over:
            on_death()
    elif state == "gameover":
        panel_t += dt
        flash = max(0.0, flash - dt * 3)
        if bird.y < GAME_HEIGHT - bird_height:      # burung jatuh setelah mati
            velocity_y += gravity
            bird.y += velocity_y
            bird.y = min(bird.y, GAME_HEIGHT - bird_height)

    # ---- gambar ----
    if state == "menu":
        draw_menu(t)
    elif state == "ready":
        draw_ready(t)
    elif state == "playing":
        draw()
    elif state == "gameover":
        draw()
        draw_game_over()
        draw_flash()
    elif state == "score":
        window.blit(background_imaege, (0, 0))
        outlined_text("Score", msg_font, (252, 160, 70), (GAME_WIDTH // 2, 150), thick=3, shadow=3)
        draw_panel(320, last_score, best_score, False)
        back_btn.draw()

    pygame.display.update()
    dt = Clock.tick(60) / 1000
