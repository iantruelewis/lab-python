# Desktop Creature v1
# v1 specification:
    # * desktop window
    # * creature represented visually
    # * game/application loop
    # * keyboard-controlled movement
    # * basic collision with window boundaries
    # * clean shutdown
###

# imports pygame library
import pygame

# configuration
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
CREATURE_RADIUS = 50
CREATURE_SPEED = 5
FPS = 60

# before using a subsystem, establish the initial state
# initialize pygame
pygame.init()

#creates application window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Desktop Creature v1")

# creates game clock
# adds predictable timing to prevent too many iterations per second
clock = pygame.time.Clock()

# creature state
creature_x = SCREEN_WIDTH // 2
creature_y = SCREEN_HEIGHT // 2

# application state
running = True

# main interactive application loop
while running:

    # INPUT -----------

    # processes events from event queue
    for event in pygame.event.get():

        # closes application if user closes window
        if event.type == pygame.QUIT:
            running = False

    # checks current keyvoard state
    keys = pygame.key.get_pressed()

    # UPDATE -----------

    # moves creature
    if keys[pygame.K_LEFT]:
        creature_x -= CREATURE_SPEED

    if keys[pygame.K_RIGHT]:
        creature_x += CREATURE_SPEED

    if keys[pygame.K_UP]:
        creature_y -= CREATURE_SPEED

    if keys[pygame.K_DOWN]:
        creature_y += CREATURE_SPEED

    # keeps creature inside window
    creature_x = max(
        CREATURE_RADIUS,
        min(creature_x, SCREEN_WIDTH - CREATURE_RADIUS))

    creature_y = max(
        CREATURE_RADIUS, 
        min(creature_y, SCREEN_HEIGHT - CREATURE_RADIUS))

    # RENDER -----------

    # clears previous frame
    screen.fill((30, 30, 30))

    # draws creature
    pygame.draw.circle(
        screen, 
        (255, 100, 100), 
        (creature_x, creature_y), 
        CREATURE_RADIUS
    )

    # displays newly rendered frame
    pygame.display.flip()

    # limits application to target frame rate
    clock.tick(FPS)

# ends application
pygame.quit()