import pygame

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

def is_in_oval(x, y, center_x, center_y, radius_x, radius_y):
    return ((x - center_x) ** 2) / (radius_x ** 2) + ((y - center_y) ** 2) / (radius_y ** 2) < 0.95

def generate_blinking_eyes(start_time):
    matrix = [[(0, 0, 0) for _ in range(WIDTH)] for _ in range(HEIGHT)]
    open_eye_color = (255, 255, 255)
    closed_eye_color = (0, 0, 0)
    elapsed_time = (pygame.time.get_ticks() - start_time) / 750

    # Create blinking effect: every 500 ms (half second) blink the eyes
    if int(elapsed_time) % 2 == 0:
        # Oval-shaped open eyes
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if is_in_oval(x, y, 22, 24, 6, 10) or is_in_oval(x, y, 42, 24, 6, 10):
                    matrix[y][x] = closed_eye_color
    else:
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if is_in_oval(x, y, 22, 24, 6, 10) or is_in_oval(x, y, 42, 24, 6, 10):
                    matrix[y][x] = open_eye_color
                    
    return matrix

# Includes the animation for closing the eyes
def generate_sleeping_eyes(start_time, closing_start_time):
    matrix = [[(0, 0, 0) for _ in range(WIDTH)] for _ in range(HEIGHT)]
    eye_color = (255, 255, 255)
    eyelid_color = (0, 0, 0)  # Black eyelid
    elapsed_time = (pygame.time.get_ticks() - start_time) / 1000
    eyelid_offset = 0
    eye_x_offset = 0 
    eye_y_offset = 0
    eyes_closed = False
    bounce_delay = 1

    # Start closing the eyes after blinking animation (adjust the start time as needed)
    start_closing_time = 4  # After X seconds, start closing (needs to by synced with blink_duartion in Main() )
    if elapsed_time >= closing_start_time:
        eyelid_offset = min(int((elapsed_time - start_closing_time) * 10), 19)  # Lower slowly over time, max 19 pixels down
        if eyelid_offset == 19:
            eyes_closed = True

    if eyes_closed:
        eye_x_offset = -4
        eye_y_offset = 8
        time_since_closed = max(0, elapsed_time - closing_start_time - bounce_delay)

        if time_since_closed >= bounce_delay:
            bounce_offset = int(elapsed_time) % 2
            eye_y_offset += bounce_offset

    # Draw the eyes first
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if is_in_oval(x, y, 22 + eye_x_offset, 24 + eye_y_offset, 6, 10) or \
                is_in_oval(x, y, 42 + eye_x_offset, 24 + eye_y_offset, 6, 10):
                matrix[y][x] = eye_color

    # Draw eyelid over the top part of the eyes
    for y in range(24 - 10 + eye_y_offset, 24 - 10 + eyelid_offset + eye_y_offset):
        for x in range(WIDTH):
            if is_in_oval(x, y, 22 + eye_x_offset, 24 + eye_y_offset, 6, 10) or \
                is_in_oval(x, y, 42 + eye_x_offset, 24 + eye_y_offset, 6, 10):
                matrix[y][x] = eyelid_color

    if eyes_closed:
        generate_zzz(matrix, elapsed_time)

    return matrix

# Generates sleeping zzz on top right
def generate_zzz(matrix, start_time, start_x = 38, start_y = 8, color = (255, 255, 255)):
    z_size = 5
    spacing = 6
    full_z_matrix = [[(0, 0, 0) for _ in range(WIDTH)] for _ in range(HEIGHT)]
    delay = 4
    elapsed_time = (pygame.time.get_ticks() - start_time) / 1000 - delay
    cycle_duration = 9
    loop_time = elapsed_time % cycle_duration
    lines_to_show = int(loop_time * 3)

    # This loop creates the entire matrix of Zs
    for i in range(3):
        z_start_y = start_y + i * spacing
        z_start_x = start_x + z_size * i

        # This loop individually creates Zs
        for j in range(z_size):
            # Top line
            if 0 <= z_start_y < HEIGHT and 0 <= z_start_x + j < WIDTH:
                full_z_matrix[z_start_y][z_start_x + j] = color

            # Diagonal line
            if 0 <= z_start_y + j < HEIGHT and 0 <= z_start_x + (z_size - 1 - j) < WIDTH:
                full_z_matrix[z_start_y + j][z_start_x + (z_size - 1 - j)] = color

            # Bottom line
            if 0 <= z_start_y + z_size - 1 < HEIGHT and 0 <= z_start_x + j < WIDTH:
                full_z_matrix[z_start_y + z_size - 1][z_start_x + j] = color

        # Turn out all of the LEDs in the Z matrix
        # Also Contains logic for showing the Zs line by line
        for y in range(HEIGHT):
            if y < lines_to_show:
                for x in range(WIDTH):
                    if full_z_matrix[y][x] != (0, 0, 0):
                        matrix[y][x] = full_z_matrix[y][x]

    return matrix


def main():
    running = True
    screen, clock = init_pygame()
    start_time = pygame.time.get_ticks()
    blink_duration = 4  # Blink for X seconds
    is_sleeping = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    is_sleeping = not is_sleeping
                    state_start_time = pygame.time.get_ticks()

        # Generate blinking eyes for blink_duration seconds
        if not is_sleeping:
            matrix = generate_blinking_eyes(start_time)
        else:
            # After blink_duration, switch to sleeping eyes (closing animation)
            matrix = generate_sleeping_eyes(start_time, 0)

        draw_matrix(screen, matrix)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
