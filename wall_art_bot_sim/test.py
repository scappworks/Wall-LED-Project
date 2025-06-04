import random
import math
import time
import board
import busio
import adafruit_veml7700
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from animations import EyeAnimations
from patterns import PatternManager


WIDTH, HEIGHT = 64, 64
FPS = 30
LIGHT_THRESHOLD = 30  # Adjust this after testing in your room

# --- Color Helpers ---
def get_cool_color():
    hue = random.randint(160, 260)  # Cool color range: blue, teal, violet
    saturation = 1.0
    value = 1.0
    return hsv_to_rgb(hue / 360.0, saturation, value)

def hsv_to_rgb(hue, saturation, value):
    hue_section = int(hue * 6)
    fractional = (hue * 6) - hue_section
    p = int(255 * value * (1 - saturation))
    q = int(255 * value * (1 - fractional * saturation))
    t = int(255 * value * (1 - (1 - fractional) * saturation))
    v = int(255 * value)

    hue_section = hue_section % 6
    if hue_section == 0:
        return (v, t, p)
    elif hue_section == 1:
        return (q, v, p)
    elif hue_section == 2:
        return (p, v, t)
    elif hue_section == 3:
        return (p, q, v)
    elif hue_section == 4:
        return (t, p, v)
    elif hue_section == 5:
        return (v, p, q)
    
def clamp_color(color):
    return max(0, min(255, int(color)))

def set_pixel(matrix, x, y, color, intensity = 1.0):
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        r, g, b = color
        matrix[y][x] = (
            clamp_color(r * intensity),
            clamp_color(g * intensity),
            clamp_color(b * intensity)
        )

# --- Pattern Functions ---
def gradient_wave_pattern():
    base_color = get_cool_color()
    matrix = [[(0, 0, 0) for _ in range(WIDTH)] for _ in range(HEIGHT)]

    for y in range(HEIGHT):
        for x in range(WIDTH):
            wave_factor = (math.sin((x + y) * 0.2) + 1) / 2
            matrix[y][x] = tuple(int(channel * wave_factor) for channel in base_color)
    return matrix

def checker_diamond_pattern():
    base_color = get_cool_color()
    matrix = [[(0, 0, 0) for _ in range(WIDTH)] for _ in range(HEIGHT)]

    for y in range(HEIGHT):
        for x in range(WIDTH):
            if ((x // 8 + y // 8) % 2) == 0:
                matrix[y][x] = base_color
    return matrix

def rug_pattern():
    matrix = [[(0, 0, 0) for _ in range(WIDTH)] for _ in range(HEIGHT)]
    stripe_width = 4
    block_height = 4
    color1 = get_cool_color()
    color2 = get_cool_color()

    for y in range(HEIGHT):
        row_color = color1 if (y // block_height) % 2 == 0 else color2

        for x in range(WIDTH):
            if ((x // stripe_width) % 2) == ((y // block_height) % 2):
                matrix[y][x] = row_color
            else:
                matrix[y][x] = tuple(c // 4 for c in row_color)  # darker version

    return matrix

def walker_pattern():
    ground_color = get_cool_color()
    sky_color = get_cool_color()
    matrix = [[(0, 0, 0) for _ in range(WIDTH)] for _ in range(HEIGHT)]
    third_height = HEIGHT // 3

    for y in range(HEIGHT):
        if y < third_height:
            color = sky_color
            cloud_centers = [
                (WIDTH // 2, HEIGHT // 5),
                (WIDTH // 2 - 4, HEIGHT // 5 + 1),
                (WIDTH // 2 + 4, HEIGHT // 5 + 1),
                (WIDTH // 2 - 2, HEIGHT // 5 - 1),
                (WIDTH // 2 + 2, HEIGHT // 5 - 1)
            ]

            radius = 4

            for x in range(WIDTH):
                for cx, cy in cloud_centers:
                    dist = math.hypot(x-cx, y-cy)
                    if dist < radius:
                        matrix[y][x] = color
        elif y < 2 * third_height:
            color = (0, 0, 0)
        else:
            color = ground_color

        if y >= third_height:
            for x in range(WIDTH):
                matrix[y][x] = color

    return matrix

# --- Pattern Manager ---
class PatternManager:
    def __init__(self):
        self.pattern_funcs = [gradient_wave_pattern, checker_diamond_pattern, rug_pattern, \
                              walker_pattern]
        self.current_matrix = [[(0, 0, 0) for _ in range(WIDTH)] for _ in range(HEIGHT)]
        self.last_pattern = None
        self.tick = 0
        self.phase = 'fade_in'
        self.base_matrix = [[(0, 0, 0) for _ in range(WIDTH)] for _ in range(HEIGHT)]
        self.phase_start_tick = 0
        self.next_pattern()

    def next_pattern(self):
        available_func = [f for f in self.pattern_funcs if f!= self.last_pattern]
        chosen_func = random.choice(available_func)
        self.base_matrix = chosen_func()
        self.last_pattern = chosen_func
        self.phase = 'fade_in'
        self.phase_start_tick = self.tick

    def update(self):
        self.tick += 1
        ticks_in_phase = self.tick - self.phase_start_tick

        if self.phase == 'fade_in':
            fade_duration = 30  # 1.5 seconds at 20 FPS
            factor = min(ticks_in_phase / fade_duration, 1.0)
            self.current_matrix = self.apply_fade(factor)
            if ticks_in_phase >= fade_duration:
                self.phase = 'hold'
                self.phase_start_tick = self.tick

        elif self.phase == 'hold':
            if ticks_in_phase >= 50:  # ~5 seconds at 20 FPS
                self.phase = 'fade_out'
                self.phase_start_tick = self.tick
            self.current_matrix = self.base_matrix

        elif self.phase == 'fade_out':
            fade_duration = 20  # ~1 second at 20 FPS
            factor = max(1.0 - (ticks_in_phase / fade_duration), 0.0)
            self.current_matrix = self.apply_fade(factor)
            if ticks_in_phase >= fade_duration:
                self.phase = 'black'
                self.phase_start_tick = self.tick

        elif self.phase == 'black':
            if ticks_in_phase >= 20:  # 1 second at 20 FPS
                self.next_pattern()
            self.current_matrix = [[(0, 0, 0) for _ in range(WIDTH)] for _ in range(HEIGHT)]

        return self.current_matrix

    def apply_fade(self, factor, gamma = 2.2):
        corrected = pow(factor, gamma)

        return [
            [tuple(clamp_color(channel * corrected) for channel in self.base_matrix[y][x]) for x in range(WIDTH)]
            for y in range(HEIGHT)
        ]



# Initialize light sensor
i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_veml7700.VEML7700(i2c)

# Setup LED matrix
options = RGBMatrixOptions()
options.rows = 64
options.cols = 64
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = 'adafruit-hat-pwm'  # or 'regular' depending on your Pi hat
matrix = RGBMatrix(options=options)

# Draw a frame to the LED matrix
def draw_matrix(matrix_data):
    for y in range(HEIGHT):
        for x in range(WIDTH):
            r, g, b = matrix_data[y][x]
            matrix.SetPixel(x, y, r, g, b)

def main():
    eye_animations = EyeAnimations()
    pattern_manager = PatternManager()

    current_mode = "blink"  # Modes: "blink", "sleep", "pattern"
    last_light_state = None
    transition_time = time.time()
    blink_start_time = time.time()

    try:
        while True:
            current_time = time.time()
            lux = sensor.lux

            # Initial blinking period
            if current_mode == "blink" and current_time - blink_start_time < 2:
                matrix_data = eye_animations.generate_blinking_eyes(blink_start_time)
            else:
                # Decide based on light sensor
                if lux < LIGHT_THRESHOLD:
                    if last_light_state != "dark":
                        transition_time = current_time
                        last_light_state = "dark"
                        current_mode = "sleep"
                    matrix_data = eye_animations.generate_sleeping_eyes(current_time, transition_time)
                else:
                    if last_light_state != "light":
                        transition_time = current_time
                        last_light_state = "light"
                        current_mode = "pattern"
                    if current_mode == "pattern":
                        matrix_data = pattern_manager.update()
                    else:
                        matrix_data = eye_animations.generate_blinking_eyes(blink_start_time)

            draw_matrix(matrix_data)
            time.sleep(1.0 / FPS)

    except KeyboardInterrupt:
        matrix.Clear()


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


if __name__ == "__main__":
    main()
