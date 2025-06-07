import random
import math

WIDTH, HEIGHT = 64, 64

def get_cool_color():
    hue = random.randint(160, 260)
    return hsv_to_rgb(hue / 360.0, 1.0, 1.0)

def hsv_to_rgb(hue, saturation, value):
    h = int(hue * 6)
    f = (hue * 6) - h
    p = int(255 * value * (1 - saturation))
    q = int(255 * value * (1 - f * saturation))
    t = int(255 * value * (1 - (1 - f) * saturation))
    v = int(255 * value)
    h %= 6
    return [(v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q)][h]

def clamp_color(value):
    return max(0, min(255, int(round(value))))

# --- Pattern Functions ---
def gradient_wave_pattern():
    base_color = get_cool_color()
    matrix = [[(0, 0, 0) for _ in range(WIDTH)] for _ in range(HEIGHT)]
    for y in range(HEIGHT):
        for x in range(WIDTH):
            wave_factor = (math.sin((x + y) * 0.2) + 1) / 2
            matrix[y][x] = tuple(clamp_color(channel * wave_factor) for channel in base_color)
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
    color1 = get_cool_color()
    color2 = get_cool_color()
    matrix = [[(0, 0, 0) for _ in range(WIDTH)] for _ in range(HEIGHT)]
    for y in range(HEIGHT):
        row_color = color1 if (y // 4) % 2 == 0 else color2
        for x in range(WIDTH):
            if ((x // 4) % 2) == ((y // 4) % 2):
                matrix[y][x] = row_color
            else:
                matrix[y][x] = tuple(c // 4 for c in row_color)
    return matrix

def walker_pattern():
    ground = get_cool_color()
    sky = get_cool_color()
    matrix = [[(0, 0, 0) for _ in range(WIDTH)] for _ in range(HEIGHT)]
    th = HEIGHT // 3

    cloud_centers = [(WIDTH//2, HEIGHT//5), (WIDTH//2-4, HEIGHT//5+1),
                     (WIDTH//2+4, HEIGHT//5+1), (WIDTH//2-2, HEIGHT//5-1),
                     (WIDTH//2+2, HEIGHT//5-1)]
    radius = 4

    for y in range(HEIGHT):
        for x in range(WIDTH):
            if y < th:
                for cx, cy in cloud_centers:
                    if math.hypot(x - cx, y - cy) < radius:
                        matrix[y][x] = sky
            elif y >= 2 * th:
                matrix[y][x] = ground
    return matrix

# --- Pattern Manager ---
class PatternManager:
    def __init__(self):
        self.pattern_funcs = [gradient_wave_pattern, checker_diamond_pattern, rug_pattern, walker_pattern]
        self.current_matrix = [[(0, 0, 0) for _ in range(WIDTH)] for _ in range(HEIGHT)]
        self.last_pattern = None
        self.tick = 0
        self.phase = 'fade_in'
        self.base_matrix = [[(0, 0, 0) for _ in range(WIDTH)] for _ in range(HEIGHT)]
        self.phase_start_tick = 0
        self.fade_cache = {}
        self.next_pattern()

    def next_pattern(self):
        self.fade_cache = {}
        available_func = [f for f in self.pattern_funcs if f != self.last_pattern]
        chosen_func = random.choice(available_func)
        self.base_matrix = chosen_func()
        self.last_pattern = chosen_func
        self.phase = 'fade_in'
        self.phase_start_tick = self.tick

    def update(self):
        self.tick += 1
        ticks_in_phase = self.tick - self.phase_start_tick

        if self.phase == 'fade_in':
            duration = 30
            factor = min(ticks_in_phase / duration, 1.0)
            self.current_matrix = self.apply_fade(factor)
            if ticks_in_phase >= duration:
                self.phase = 'hold'
                self.phase_start_tick = self.tick

        elif self.phase == 'hold':
            if ticks_in_phase >= 50:
                self.phase = 'fade_out'
                self.phase_start_tick = self.tick
            self.current_matrix = self.base_matrix

        elif self.phase == 'fade_out':
            duration = 30
            factor = max(1.0 - (ticks_in_phase / duration), 0.05)
            self.current_matrix = self.apply_fade(factor)
            if ticks_in_phase >= duration:
                self.phase = 'black'
                self.phase_start_tick = self.tick

        elif self.phase == 'black':
            if ticks_in_phase >= 20:
                self.next_pattern()
            self.current_matrix = self.apply_fade(0.05)

        return self.current_matrix

    def apply_fade(self, factor, gamma=3.0):
        cache_key = round(factor, 3)
        if cache_key in self.fade_cache:
            return self.fade_cache[cache_key]
        
        corrected = pow(factor, gamma)

        faded = [
            [tuple(clamp_color(channel * corrected) for channel in self.base_matrix[y][x])
             for x in range(WIDTH)]
            for y in range(HEIGHT)
        ]

        return faded
