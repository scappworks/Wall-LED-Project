# animations.py
import pygame

WIDTH, HEIGHT = 64, 64
SCALE = 8

class EyeAnimations:
    def __init__(self):
        self.open_eye_color = (255, 255, 255)
        self.closed_eye_color = (0, 0, 0)
    
    def is_in_oval(self, x, y, center_x, center_y, radius_x, radius_y):
        return ((x - center_x) ** 2) / (radius_x ** 2) + ((y - center_y) ** 2) / (radius_y ** 2) < 0.95
    
    def generate_blinking_eyes(self, start_time):
        matrix = [[(0, 0, 0) for _ in range(WIDTH)] for _ in range(HEIGHT)]
        elapsed_time = (pygame.time.get_ticks() - start_time) / 750

        # Create blinking effect: every 500 ms (half second) blink the eyes
        if int(elapsed_time) % 2 == 0:
            # Oval-shaped closed eyes
            for y in range(HEIGHT):
                for x in range(WIDTH):
                    if self.is_in_oval(x, y, 22, 24, 6, 10) or self.is_in_oval(x, y, 42, 24, 6, 10):
                        matrix[y][x] = self.closed_eye_color
        else:
            for y in range(HEIGHT):
                for x in range(WIDTH):
                    if self.is_in_oval(x, y, 22, 24, 6, 10) or self.is_in_oval(x, y, 42, 24, 6, 10):
                        matrix[y][x] = self.open_eye_color

        return matrix

    def generate_sleeping_eyes(self, start_time, zzz_start_time):
        matrix = [[(0, 0, 0) for _ in range(WIDTH)] for _ in range(HEIGHT)]
        elapsed_time = (pygame.time.get_ticks() - start_time) / 1000
        eyelid_offset = min(int((elapsed_time) * 10), 19)  # Lower eyelids slowly over time
        eyes_closed = eyelid_offset == 19

        eye_x_offset, eye_y_offset = 0, 0
        bounce_delay = 1
        if eyes_closed:
            eye_x_offset = -4
            eye_y_offset = 8
            time_since_closed = max(0, elapsed_time - bounce_delay)
            if time_since_closed >= bounce_delay:
                bounce_offset = int(elapsed_time) % 2
                eye_y_offset += bounce_offset

        # Draw the eyes
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if self.is_in_oval(x, y, 22 + eye_x_offset, 24 + eye_y_offset, 6, 10) or \
                   self.is_in_oval(x, y, 42 + eye_x_offset, 24 + eye_y_offset, 6, 10):
                    matrix[y][x] = self.open_eye_color

        # Draw eyelid over the top part of the eyes
        for y in range(24 - 10 + eye_y_offset, 24 - 10 + eyelid_offset + eye_y_offset):
            for x in range(WIDTH):
                if self.is_in_oval(x, y, 22 + eye_x_offset, 24 + eye_y_offset, 6, 10) or \
                   self.is_in_oval(x, y, 42 + eye_x_offset, 24 + eye_y_offset, 6, 10):
                    matrix[y][x] = self.closed_eye_color

        if eyes_closed:
            self.generate_zzz(matrix, zzz_start_time)

        return matrix

    def generate_zzz(self, matrix, start_time, start_x=38, start_y=8, color=(255, 255, 255)):
        z_size = 5
        spacing = 6
        full_z_matrix = [[(0, 0, 0) for _ in range(WIDTH)] for _ in range(HEIGHT)]
        elapsed_time = (pygame.time.get_ticks() - start_time) / 1000
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

            # Turn off all of the LEDs in the Z matrix.
            # Also contains logic for showing the Zs line by line
            for y in range(HEIGHT):
                if y < lines_to_show:
                    for x in range(WIDTH):
                        if full_z_matrix[y][x] != (0, 0, 0):
                            matrix[y][x] = full_z_matrix[y][x]

        return matrix
