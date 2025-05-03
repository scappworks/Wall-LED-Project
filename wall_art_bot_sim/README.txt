
Wall Art Bot Simulator (Windows) - Getting Started
===================================================

This simulator helps you prototype animations for your LED matrix project on Windows using Pygame.

FILES:
- main.py: Simulator that shows a simple blinking eyes animation with Zzzs.
- README.txt: This file.

REQUIREMENTS:
- Python 3.x
- Pygame library

INSTALLATION:
1. Install Python from https://python.org if not already installed.
2. Open a command prompt and install Pygame:
   pip install pygame

RUNNING THE SIMULATOR:
- Navigate to this folder in command prompt.
- Run the simulator:
  python main.py

WHAT'S NEXT:
=============
Once your Raspberry Pi and LED matrix arrive:
1. Install the `rpi-rgb-led-matrix` library:
   https://github.com/hzeller/rpi-rgb-led-matrix

2. Use similar logic as in main.py, but instead of Pygame's draw_matrix(),
   you'll use the RGBMatrix API to draw pixels.

Happy prototyping!
