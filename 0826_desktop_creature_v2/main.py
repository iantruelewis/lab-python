# Desktop Creature v2
# v2 specification:
    # * mouse interaction
    # * keyboard movement
    # * autonomous wandering
    # * behavioral states
    # * creature class
    # * separated movement logic
    # * separated state behavior
# # #


# imports
import math
import random
import pygame


# configuration
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
CREATURE_RADIUS = 50
CREATURE_SPEED = 5
FPS = 60

WANDER_INTERVAL = 2.0
WANDER_DURATION = 1.5


# creature states
IDLE = "idle"
WANDER = "wander"
FOLLOW = "follow"


class Creature:

    def __init__(self):

        # position
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2

        # behavioral state
        self.state = IDLE

        # wandering state
        self.wander_timer = 0
        self.wander_duration_timer = 0

        self.wander_dx = 0
        self.wander_dy = 0


    def update(self, dt, mouse_position, mouse_pressed, keys):

        # gets mouse position
        mouse_x, mouse_y = mouse_position

        # checks whether left mouse is pressed
        left_mouse_pressed = mouse_pressed[0]

        # determines whether a movement key is being held
        keyboard_is_pressed = (
            keys[pygame.K_LEFT]
            or keys[pygame.K_RIGHT]
            or keys[pygame.K_UP]
            or keys[pygame.K_DOWN]
        )


        # follow
        # mouse input has highest priority
        if left_mouse_pressed:

            self.state = FOLLOW

            self.update_follow(mouse_position)


        # keyboard
        # keyboard input overrides autonomous behavior
        elif keyboard_is_pressed:
        
            self.state = IDLE

            # creates keyboard direction
            input_dx = 0
            input_dy = 0

            # moves creature
            if keys[pygame.K_LEFT]:
                input_dx -= 1
        
            if keys[pygame.K_RIGHT]:
                input_dx += 1
        
            if keys[pygame.K_UP]:
                input_dy -= 1
        
            if keys[pygame.K_DOWN]:
                input_dy += 1

            # calculates magnitude of keyboard direction
            distance = math.sqrt(
                input_dx ** 2 + input_dy ** 2
            )

            if distance > 0:

                input_dx /= distance
                input_dy /= distance

                self.move(input_dx, input_dy)


        # wander
        elif self.state == WANDER:

            self.update_wander(dt)

        # idle behavior
        else:

            self.state = IDLE
            self.update_idle(dt)

        # keeps creature inside window
        self.constrain_to_screen()


    def update_follow(self, mouse_position):

        # gets mouse position
        mouse_x, mouse_y = mouse_position

        # calculates vector from creature to mouse
        dx = mouse_x - self.x
        dy = mouse_y - self.y

        # calculates distance to mouse
        distance = math.sqrt(dx ** 2 + dy ** 2)

        # prevents division by zero
        if distance > 0:

            # normalizes direction vector
            direction_x = dx / distance
            direction_y = dy / distance

            # move toward mouse
            self.move(direction_x, direction_y)


    def update_wander(self, dt):

        # updates wandering timer
        self.wander_duration_timer += dt

        # moves in current wandering direction
        self.move(
            self.wander_dx,
            self.wander_dy
        )

        # ends wandering after duration
        if self.wander_duration_timer >=WANDER_DURATION:

            self.state = IDLE
            self.wander_duration_timer = 0


    def update_idle(self, dt):

            # updates idle timer
            self.wander_timer += dt

            # checks whether it is time to consider wandering
            if self.wander_timer >= WANDER_INTERVAL:

                # randomly decides whether to wander
                if random.random() < 0.5:

                    self.state = WANDER
                    self.wander_duration_timer = 0

                    # chooses a random direction
                    self.wander_dx = random.uniform(-1, 1)
                    self.wander_dy = random.uniform(-1, 1)

                    # calculates magnitude of random direction
                    distance = math.sqrt(
                        self.wander_dx ** 2 +
                        self.wander_dy ** 2
                    )

                    # normalizes direction vector
                    if distance > 0:

                        self.wander_dx /= distance
                        self.wander_dy /= distance

                # resets idle timer
                self.wander_timer = 0


    def move(self, direction_x, direction_y):

        self.x += direction_x * CREATURE_SPEED
        self.y += direction_y * CREATURE_SPEED


    def constrain_to_screen(self):

        # constrains horizontal position
        self.x = max (
            CREATURE_RADIUS,
            min(self.x, SCREEN_WIDTH - CREATURE_RADIUS)
        )

        # constrains vertical position
        self.y = max (
                    CREATURE_RADIUS,
                    min(self.y, SCREEN_HEIGHT - CREATURE_RADIUS)
                )


    def draw(self, screen):

        # draws creature
        pygame.draw.circle(
            screen,
            (255, 100, 100),
            (self.x, self.y),
            CREATURE_RADIUS
        )


# input
def handle_events():

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            return False

    return True


# initializes pygame
pygame.init()

# creates application window
screen = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT)
    )

pygame.display.set_caption("Desktop Creature")

# creates game clock
# adds predictable timing to prevent too many iterations per second
clock = pygame.time.Clock()

# creates creature
creature = Creature()

# application state
running = True


# main loop
while running:

    # calculates elapsed time in seconds
    dt = clock.tick(FPS) / 1000

    # input
    running = handle_events()

    mouse_position = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()
    keys = pygame.key.get_pressed()

    # update
    creature.update(
        dt,
        mouse_position,
        mouse_pressed,
        keys
    )

    # render
    screen.fill((30, 30, 30))

    creature.draw(screen)

    pygame.display.flip()


# shutdown pygame
pygame.quit()