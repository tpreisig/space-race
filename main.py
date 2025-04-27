# 0
import pygame

# 1
pygame.init()

# 2
screen = pygame.display.set_mode((900, 500))

# 3
clock = pygame.time.Clock()

# 4
running = True

# 5
while running:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
    elif event.type == pygame.KEYDOWN:
      if event.key == pygame.K_ESCAPE:
        running = False
      elif event.key == pygame.K_UP:
        screen.fill("green")
        pygame.display.flip()
      elif event.key == pygame.K_DOWN:
        screen.fill("red")
      else:
        screen.fill("sky blue")
        pygame.display.flip()

# 6

# 7 

# 8
clock.tick(60)

pygame.quit()
