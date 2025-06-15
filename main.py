from os.path import join
import pygame
import random
import pygame.freetype
import config

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Setup screen and clock
screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
pygame.display.set_caption("Space Race")
clock = pygame.time.Clock()

gradient_surface = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))

# Function to create a linear gradient for a background fill
def create_linear_gradient(surface, start_color, end_color):
    width, height = surface.get_size()
    # Interpolate colors for each row
    for y in range(height):
        # Calculate the interpolation factor (0 at top, 1 at bottom)
        t = y / (height - 1)
        # Linearly interpolate between start_color and end_color
        r = int(start_color[0] + t * (end_color[0] - start_color[0]))
        g = int(start_color[1] + t * (end_color[1] - start_color[1]))
        b = int(start_color[2] + t * (end_color[2] - start_color[2]))
        # Draw a horizontal line at this y-coordinate with the interpolated color
        pygame.draw.line(surface, (r, g, b), (0, y), (width - 1, y))

# Generate the gradient once (since it doesn't change)
create_linear_gradient(gradient_surface, config.COLOR_START, config.COLOR_END)

# Load assets

def rocket_surface():
    rocket = pygame.image.load(join("images", "rocket.png"))
    return rocket

def collect_it():
    col1 = pygame.image.load(join("images", "coll1.png"))
    col2 = pygame.image.load(join("images", "coll2.png"))
    col3 = pygame.image.load(join("images", "coll3.png"))
    col4 = pygame.image.load(join("images", "coll4.png"))
    col5 = pygame.image.load(join("images", "coll5.png"))
    col6 = pygame.image.load(join("images", "coll6.png"))
    col7 = pygame.image.load(join("images", "coll7.png"))
    col8 = pygame.image.load(join("images", "coll8.png"))
    return random.choice([col1, col2, col3, col4, col5, col6, col7, col8])

def create_asteroid():
    meteor = pygame.image.load((join("images", "meteor.png")))
    return meteor

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
        self.image = rocket_surface()
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

class Collectables(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = collect_it()
        self.rect = self.image.get_rect(center=(random.randint(0, config.SCREEN_WIDTH), 0))
        self.speed = config.COLLECTABLES_SPEED

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > config.SCREEN_HEIGHT:
            self.kill()  # Remove if off-screen

class Asteroid(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = create_asteroid()
        self.rect = self.image.get_rect(center=(random.randint(0, config.SCREEN_WIDTH), 0))
        self.speed = config.ASTEROID_SPEED

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > config.SCREEN_HEIGHT:
            self.kill()  # Remove if off-screen

# Sprite groups
all_sprites = pygame.sprite.Group()
collectables_group = pygame.sprite.Group()
asteroid_group = pygame.sprite.Group()

# Game variables
player = Player()
all_sprites.add(player)
score = 0
running = True
game_over = False
game_over_time = None
collectables_timer = 0
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
                    collectables_group.empty()
                    asteroid_group.empty()
                    all_sprites.add(player)
                    score = 0
                    game_over = False
                    game_over_time = None
                    collectables_timer = 0
                    asteroid_timer = 0

    if not game_over:
        # Update
        current_time = pygame.time.get_ticks()
        # Spawn collectables
        if current_time - collectables_timer > config.COLLECTABLES_SPAWN_RATE:
            collectables = Collectables()
            all_sprites.add(collectables)
            collectables_group.add(collectables)
            collectables_timer = current_time
        # Spawn asteroids
        if current_time - asteroid_timer > config.ASTEROID_SPAWN_RATE:
            asteroid = Asteroid()
            all_sprites.add(asteroid)
            asteroid_group.add(asteroid)
            asteroid_timer = current_time

        all_sprites.update()

        # Collisions
        if pygame.sprite.spritecollide(player, collectables_group, True):  # Collect them
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
        screen.blit(gradient_surface, (0, 0))
        all_sprites.draw(screen)
        # Draw score
        font.render_to(screen, (10, 10), f"Score: {score}", config.TEXT_COLOR)
        # Draw health bar
        health_rect = pygame.Rect(10, 50, player.health * 2, 20)
        pygame.draw.rect(screen, config.HEALTH_BAR_COLOR, health_rect)
        pygame.draw.rect(screen, config.TEXT_COLOR, (10, 50, 200, 20), 2)  # Border

    else:
        # Game over screen
        screen.blit(gradient_surface, (0, 0))
        font.render_to(screen, (config.SCREEN_WIDTH // 2 - 180, config.SCREEN_HEIGHT // 2 - 20),
                       f"Game Over! Score: {score}", config.TEXT_COLOR)
        if pygame.time.get_ticks() - game_over_time > 2000:
            font.render_to(screen, (config.SCREEN_WIDTH // 2 - 180, config.SCREEN_HEIGHT // 2 + 20),
                           "Press R to Restart", config.TEXT_COLOR)

    pygame.display.flip()
    clock.tick(config.FPS)


pygame.quit()
