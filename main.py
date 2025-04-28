
import pygame
import random
import pygame.freetype
import config

# Initializing the game
pygame.init()
pygame.mixer.init()

# Setup screen and clock
screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
pygame.display.set_caption("Space Race")
clock = pygame.time.Clock()

# Load assets
# Placeholder: Use rectangles/circles; replace with images in real game
def create_player_surface():
    surf = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.polygon(surf, config.PLAYER_COLOR, [(20, 0), (0, 40), (40, 40)])  # Triangle
    return surf

def create_debris_surface():
    surf = pygame.Surface((20, 20), pygame.SRCALPHA)
    pygame.draw.circle(surf, config.DEBRIS_COLOR, (10, 10), 10)  # Circle
    return surf

def create_asteroid_surface():
    surf = pygame.Surface((30, 30), pygame.SRCALPHA)
    pygame.draw.rect(surf, config.ASTEROID_COLOR, (0, 0, 30, 30))  # Square
    return surf

# Load sounds (replace with your file paths)
try:
    score_up = pygame.mixer.Sound("sound/score_up.mp3")
    hit_sound = pygame.mixer.Sound("sound/sound_alert.mp3")
    pygame.mixer.music.load("sound/sound.mp3")
    pygame.mixer.music.play(-1)  # Loop indefinitely
except FileNotFoundError:
    print("Audio not found. Running game without sound.")
    score_up = None
    hit_sound = None

# Font
font = pygame.freetype.SysFont(None, 36)

# Sprite classes
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = create_player_surface()
        self.rect = self.image.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2))
        self.health = 100

    def update(self):
        # Movement with arrow keys or WASD
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= config.PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += config.PLAYER_SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= config.PLAYER_SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += config.PLAYER_SPEED
        self.rect.x += dx
        self.rect.y += dy
        # Keep player in bounds
        self.rect.clamp_ip(screen.get_rect())

class Debris(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = create_debris_surface()
        self.rect = self.image.get_rect(center=(random.randint(0, config.SCREEN_WIDTH), 0))
        self.speed = config.DEBRIS_SPEED

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > config.SCREEN_HEIGHT:
            self.kill()  # Remove if off-screen

class Asteroid(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = create_asteroid_surface()
        self.rect = self.image.get_rect(center=(random.randint(0, config.SCREEN_WIDTH), 0))
        self.speed = config.ASTEROID_SPEED

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > config.SCREEN_HEIGHT:
            self.kill()  # Remove if off-screen

# Sprite groups
all_sprites = pygame.sprite.Group()
debris_group = pygame.sprite.Group()
asteroid_group = pygame.sprite.Group()

# Game variables
player = Player()
all_sprites.add(player)
score = 0
running = True
game_over = False
game_over_time = None
debris_timer = 0
asteroid_timer = 0

# Main game loop
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif game_over and pygame.time.get_ticks() - game_over_time > 2000:
                if event.key == pygame.K_r:  # Restart on 'R'
                    # Reset game
                    player = Player()
                    all_sprites.empty()
                    debris_group.empty()
                    asteroid_group.empty()
                    all_sprites.add(player)
                    score = 0
                    game_over = False
                    game_over_time = None
                    debris_timer = 0
                    asteroid_timer = 0

    if not game_over:
        # Update
        current_time = pygame.time.get_ticks()
        # Spawn debris
        if current_time - debris_timer > config.DEBRIS_SPAWN_RATE:
            debris = Debris()
            all_sprites.add(debris)
            debris_group.add(debris)
            debris_timer = current_time
        # Spawn asteroids
        if current_time - asteroid_timer > config.ASTEROID_SPAWN_RATE:
            asteroid = Asteroid()
            all_sprites.add(asteroid)
            asteroid_group.add(asteroid)
            asteroid_timer = current_time

        all_sprites.update()

        # Collisions
        if pygame.sprite.spritecollide(player, debris_group, True):  # Collect debris
            score += 10
            if score_up:
                score_up.play()
        if pygame.sprite.spritecollide(player, asteroid_group, True):  # Hit asteroid
            player.health -= 20
            if hit_sound:
                hit_sound.play()
            if player.health <= 0:
                game_over = True
                game_over_time = pygame.time.get_ticks()

        # Draw
        screen.fill(config.BG_COLOR)
        all_sprites.draw(screen)
        # Draw score
        font.render_to(screen, (10, 10), f"Score: {score}", config.TEXT_COLOR)
        # Draw health bar
        health_rect = pygame.Rect(10, 50, player.health * 2, 20)
        pygame.draw.rect(screen, config.HEALTH_BAR_COLOR, health_rect)
        pygame.draw.rect(screen, config.TEXT_COLOR, (10, 50, 200, 20), 2)  # Border

    else:
        # Game over screen
        screen.fill(config.BG_COLOR)
        font.render_to(screen, (config.SCREEN_WIDTH // 2 - 100, config.SCREEN_HEIGHT // 2 - 20),
                       f"Game Over! Score: {score}", config.TEXT_COLOR)
        if pygame.time.get_ticks() - game_over_time > 2000:
            font.render_to(screen, (config.SCREEN_WIDTH // 2 - 100, config.SCREEN_HEIGHT // 2 + 20),
                           "Press R to Restart", config.TEXT_COLOR)

    pygame.display.flip()
    clock.tick(config.FPS)

pygame.quit()