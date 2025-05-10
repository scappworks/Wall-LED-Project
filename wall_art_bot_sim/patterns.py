import random
import math

WIDTH, HEIGHT = 64, 64

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
    
def set_pixel(matrix, x, y, color, intensity = 1.0):
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        r, g, b = color
        matrix[y][x] = (
            int (r * intensity),
            int(g * intensity),
            int(b * intensity)
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

    for y in range(HEIGHT):
        row_color = get_cool_color() if (y // block_height) % 2 == 0 else get_cool_color()

        for x in range(WIDTH):
            if ((x // stripe_width) % 2) == ((y // block_height) % 2):
                matrix[y][x] = row_color
            else:
                matrix[y][x] = tuple(c // 4 for c in row_color)  # darker version

    return matrix



# --- Pattern Manager ---
class PatternManager:
    def __init__(self):
        self.pattern_funcs = [gradient_wave_pattern, checker_diamond_pattern, rug_pattern]
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

    def apply_fade(self, factor):
        return [
            [tuple(int(channel * factor) for channel in self.base_matrix[y][x]) for x in range(WIDTH)]
            for y in range(HEIGHT)
        ]
