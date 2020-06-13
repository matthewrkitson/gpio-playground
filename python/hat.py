import curses
import colorzero
import gpiozero
import sys
import time
import threading

from log import logger

buzzer = gpiozero.TonalBuzzer(2)

green = gpiozero.PWMLED(14)
yellow = gpiozero.PWMLED(18)
orange = gpiozero.PWMLED(23)
red = gpiozero.PWMLED(19)
blue = gpiozero.PWMLED(8)

rgb1 = gpiozero.RGBLED(12, 25, 26)
rgb2 = gpiozero.RGBLED(20, 21, 16)

button1 = gpiozero.Button(17)
button2 = gpiozero.Button(27)
button3 = gpiozero.Button(22)

switch1 = gpiozero.Button(13)
switch2 = gpiozero.Button(6)
switch3 = gpiozero.Button(5)

tilt1 = gpiozero.Button(9)
tilt2 = gpiozero.Button(4, pull_up=True)

ldr = gpiozero.LightSensor(10)
pot = gpiozero.LightSensor(11)

def draw_led(stdscr, y, x, led, name, colour):
    stdscr.addstr(y, x, "(")
    if (led.value > 0.5):
        stdscr.addstr(" ", curses.A_REVERSE | colour)
    else:
        stdscr.addstr(" ")
    stdscr.addstr(") ")
    stdscr.addstr(name, colour)

def draw_bar(stdscr, width, value, colour):
    stdscr.addstr("[")
    fill = int(width * value)
    stdscr.addstr(" " * fill, curses.A_REVERSE | colour)
    stdscr.addstr(" " * (width - fill))
    stdscr.addstr("]")

def draw_pwmled(stdscr, y, x, led, name, colour):
    if isinstance(led, gpiozero.PWMLED):
        value = led.value
    else:
        value = led
    stdscr.addstr(y, x, name + " ", colour)
    draw_bar(stdscr, 20, value, colour)

def draw_rgbled(stdscr, y, x, led, name, colours):
    stdscr.addstr(y, x, name)
    (r, g, b) = led.value
    draw_pwmled(stdscr, y+1, x, r, "R", colours["red"])
    draw_pwmled(stdscr, y+2, x, g, "G", colours["green"])
    draw_pwmled(stdscr, y+3, x, b, "B", colours["blue"])

def draw_screen(stdscr, colours, state):
    stdscr.erase()
    header =  "{:^80}".format("---- gpio-playground status display     " + time.strftime("%x %X") + " ----")
    stdscr.addstr(0, 0, header, curses.A_REVERSE)
    draw_led(stdscr,  2, 2, green,  "Green",  colours["green"])
    draw_led(stdscr,  3, 2, yellow, "Yellow", colours["yellow"])
    draw_led(stdscr,  4, 2, orange, "Orange", colours["orange"])
    draw_led(stdscr,  5, 2, red,    "Red",    colours["red"])
    
    draw_pwmled(stdscr, 7, 2, blue, "Blue", colours["blue"])

    draw_rgbled(stdscr, 9, 2, rgb1, "RGB-1", colours)
    draw_rgbled(stdscr, 14, 2, rgb2, "RGB-2", colours)
    stdscr.refresh()

def run_update_loop(stdscr):
    logger.debug("Starting display update loop")
    
    curses.curs_set(False)
    stdscr.nodelay(True)
    
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)  
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)  
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)  
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)  
    curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_BLACK)  

    colours = {}
    colours["green"] = curses.color_pair(1)
    colours["yellow"] = curses.color_pair(2)
    colours["orange"] = curses.color_pair(3)
    colours["red"] = curses.color_pair(4)
    colours["blue"] = curses.color_pair(5)

    state = {}
    state["exit_requested"] = False

    while not state["exit_requested"]:
        handle_input(stdscr, state)
        draw_screen(stdscr, colours, state)
        time.sleep(0.1)

def handle_input(stdscr, state):
    c = stdscr.getch()
    if c == ord("q"):
        state["exit_requested"] = True

def safe(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except KeyboardInterrupt:
            logger.debug("Keyboard interrupt: exiting.")
        except BaseException as e:
            logger.exception(e)
    
    logger.debug("Wrapping " + str(func) + " to log exceptions.")
    return wrapper 

def binary_lights():
    logger.debug("Starting binary lights")
    while True:
        for i in range(16):
            green.value =  bool(i & 0b00000001)
            yellow.value = bool(i & 0b00000010)
            orange.value = bool(i & 0b00000100)
            red.value =    bool(i & 0b00001000)

            time.sleep(0.5)

def colour_cycle(rgbled):
    logger.debug("Starting colour cycle for " + str(rgbled))
    red  = colorzero.Color("red")
    while True:
        for i in range(360):
            rgbled.color = red + colorzero.Hue(deg=i)
            time.sleep(0.1)

def main(stdscr): 
    logger.debug("Starting threads.")
    blue.pulse(fade_in_time=0.5, fade_out_time=0.5)
    threading.Thread(target=safe(binary_lights), name="binary", daemon=True).start()
    threading.Thread(target=safe(colour_cycle), name="colour cycle", args=[rgb1], daemon=True).start()
    
    run_update_loop(stdscr)

curses.wrapper(safe(main))
