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

# Initialize light sensor
i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_veml7700.VEML7700(i2c)

# Setup LED matrix
options = RGBMatrixOptions()
options.rows = 64
options.cols = 64
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = 'adafruit-hat'  # or 'regular' depending on your Pi hat
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

if __name__ == "__main__":
    main()
