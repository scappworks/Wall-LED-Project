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

# Function to generate blinking eyes for 3 seconds
def generate_blinking_eyes(start_time, blink_duration):
    matrix = [[(0, 0, 0) for _ in range(WIDTH)] for _ in range(HEIGHT)]
    eye_color = (255, 255, 255)
    elapsed_time = (pygame.time.get_ticks() - start_time) / 750

    # Start with open eyes, blink, and return to open eyes
    if elapsed_time < blink_duration:
        # Create blinking effect: every 500 ms (half second) blink the eyes
        if int(elapsed_time) % 2 == 0: 
            # Oval-shaped open eyes
            for y in range(HEIGHT):
                for x in range(WIDTH):
                    if is_in_oval(x, y, 22, 24, 6, 10) or is_in_oval(x, y, 42, 24, 6, 10):
                        matrix[y][x] = eye_color
    else:
        # After 3 seconds, leave the eyes open
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if is_in_oval(x, y, 22, 24, 6, 10) or is_in_oval(x, y, 42, 24, 6, 10):
                    matrix[y][x] = eye_color
    return matrix

# Function to generate sleeping eyes (closing state)
def generate_sleeping_eyes(start_time, closing_start_time):
    matrix = [[(0, 0, 0) for _ in range(WIDTH)] for _ in range(HEIGHT)]
    eye_color = (255, 255, 255)
    eyelid_color = (0, 0, 0)  # Black eyelid
    elapsed_time = (pygame.time.get_ticks() - start_time) / 1000
    eyelid_offset = 0
    eye_x_offset = 0 
    eye_y_offset = 0
    eyes_closed = False

    # Start closing the eyes after blinking animation (adjust the start time as needed)
    start_closing_time = 4  # After 3 seconds, start closing (once blink duration is done)
    if elapsed_time >= closing_start_time:
        eyelid_offset = min(int((elapsed_time - start_closing_time) * 10), 19)  # Lower slowly over time, max 19 pixels down
        if eyelid_offset >= 19:
            eyes_closed = True

    if eyes_closed:
        eye_x_offset = -2
        eye_y_offset = 2

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

    return matrix

def main():
    running = True
    screen, clock = init_pygame()
    start_time = pygame.time.get_ticks()
    blink_duration = 4  # Blink for 3 seconds
    closing_start_time = blink_duration

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Generate blinking eyes for 3 seconds
        if (pygame.time.get_ticks() - start_time) / 1000 < blink_duration:
            matrix = generate_blinking_eyes(start_time, blink_duration)
        else:
            # After blinking duration, switch to sleeping eyes (closing animation)
            matrix = generate_sleeping_eyes(start_time, closing_start_time)

        draw_matrix(screen, matrix)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
