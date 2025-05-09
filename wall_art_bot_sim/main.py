import pygame
from animations import EyeAnimations

WIDTH, HEIGHT = 64, 64
SCALE = 8
FPS = 30

# Initialize Pygame
def init_pygame():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH * SCALE, HEIGHT * SCALE))
    pygame.display.set_caption("Wall Art Bot Simulator")
    clock = pygame.time.Clock()
    return screen, clock

def draw_matrix(screen, matrix):
    for y in range(HEIGHT):
        for x in range(WIDTH):
            color = matrix[y][x]
            pygame.draw.rect(screen, color, (x*SCALE, y*SCALE, SCALE, SCALE))

def main():
    running = True
    screen, clock = init_pygame()
    start_time = pygame.time.get_ticks()
    zzz_start_time = pygame.time.get_ticks()
    is_sleeping = False
    eye_animations = EyeAnimations()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    is_sleeping = not is_sleeping
                    start_time = pygame.time.get_ticks()
                    zzz_start_time = pygame.time.get_ticks()

        if not is_sleeping:
            matrix = eye_animations.generate_blinking_eyes(start_time)
        else:
            matrix = eye_animations.generate_sleeping_eyes(start_time, zzz_start_time)

        draw_matrix(screen, matrix)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
