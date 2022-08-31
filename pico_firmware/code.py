from time import sleep
import board
import busio
import neopixel
from keypad import KeyMatrix
from digitalio import DigitalInOut, Direction, Pull
import rotaryio
from analogio import AnalogIn
import random
# import storage 
import displayio
import terminalio
from adafruit_display_text import label
import adafruit_displayio_ssd1306


class CustomDisplay:
    def __init__(self):
        displayio.release_displays()
        i2c = busio.I2C(board.GP5, board.GP4)
        display_bus = displayio.I2CDisplay(i2c, device_address=0x3c)
        self._display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=32)
        self._splash = displayio.Group()
        self._text = ""
        self._text_changed = True

        # Make the display context
        self._display.show(self._splash)
        color_bitmap = displayio.Bitmap(128, 32, 1)
        color_palette = displayio.Palette(1)
        color_palette[0] = 0xFFFFFF  # White

        bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
        self._splash.append(bg_sprite)
        # Draw a smaller inner rectangle as text background
        inner_bitmap = displayio.Bitmap(118, 24, 1)
        inner_palette = displayio.Palette(1)
        inner_palette[0] = 0x000000  # Black
        inner_sprite = displayio.TileGrid(inner_bitmap, pixel_shader=inner_palette, x=5, y=4)
        self._splash.append(inner_sprite)    
        # Draw a label
        self._text_area = label.Label(terminalio.FONT, text=self._text, color=0xFFFFFF, x=28, y=15)
        self._splash.append(self._text_area)

    def text(self, text):
        self._text = text
        self._text_changed = True

    def update(self):
        if not self._text_changed:
            return
        self._text_changed = False
        self._text_area.text = self._text
        self._display.show(self._splash)

    def close(self):
        displayio.release_displays()

display = CustomDisplay()



pixels = neopixel.NeoPixel(board.GP0, 13, brightness=0.3, auto_write=True)  # does not need pixels.show() each time
l2b = (0, 1, 2, 3, 4, 8, 7, 6, 5, 9, 10, 11, 12)  # led index map with button index


# CUSTOM FUNCTIONS FOR POTENTIOMETERS ===============================

def change_brightness(val):
    # val 0.0 to 1.0
    pixels.brightness = round(val, 3)
    print(f"brightness {pixels.brightness}")

last_volume = 0
def change_volume(val):
    # val 0.0 to 1.0
    global last_volume
    volume = round(val*10)
    if volume == last_volume:
        return
    last_volume = volume
    m = f"vol {volume}"
    print(m)
    display.text(m)

last_example = 0
def change_example(val):
    # val 0.0 to 1.0
    global last_example
    disc_value = round(val*50)
    if disc_value == last_example:
        return
    last_example = disc_value
    m = f"exam {disc_value}"
    print(m)
    display.text(m)

pots = []
pots.append({
    "id": 1,
    'apin': AnalogIn(board.GP27_A1),
    'min': 3872,  # TODO get from configuration file
    'max': 62272,
    'threshold': 1200,
    'divisions': 10,
    'inverted': True,
    'trigger_at_start': False,
    'callback': change_volume,
})
pots.append({
    "id": 2,
    'apin': AnalogIn(board.GP28_A2),
    'min': 4256 + 450, # measured 4256
    'max': 62704 - 600, # measured 62704
    'threshold': 1200,
    'divisions': 20,
    'inverted': True,
    'trigger_at_start': True,
    'callback': change_brightness,    
})
pots.append({
    "id": 3,
    'apin': AnalogIn(board.GP26_A0),
    'min': 144 + 450,  # measured 144
    'max': 65520 - 450, # measured 65520
    'threshold': 900,
    'divisions': 10,
    'inverted': True,
    'trigger_at_start': False,
    'callback': change_example,
})

# configure pots
for pot in pots:
    sleep(0.01)
    if pot['trigger_at_start']:
        pot['last_value'] = 99999
    else:
        pot['last_value'] = pot['apin'].value


encoders = []
encoders.append({
    "id": 1,
    'obj': rotaryio.IncrementalEncoder(board.GP12, board.GP11),
    'last_position': 0
})

# configure and fill last_position
for encoder in encoders:
    encoder['obj'].divisor = 2
    encoder['last_position'] = encoder['obj'].position


km = KeyMatrix(
    row_pins=(board.GP20, board.GP19, board.GP18),
    column_pins=(board.GP16, board.GP17, board.GP21, board.GP22),
    # interval=0.050,  # debounce
)


def check_pots():
    for pot in pots:
        value = pot['apin'].value
        if abs(value - pot['last_value']) > pot['threshold']:
            # v = value * 3.3 / 65536
            pot['last_value'] = value
            d = (value - pot['min'])/(pot['max'] - pot['min'])
            if d<0:
                d=0.0
            elif d>1:
                d=1.0
            if pot['inverted']:
                d=1.0-d
            print(f"pot id {pot['id']}: raw {value} norm {d:.3f}")
            # display.text(f"p{pot['id']}: {d:.2f}")
            pot['callback'](d)


def check_encoders():
    for encoder in encoders:
        position = encoder['obj'].position
        if position != encoder['last_position']:
            encoder['last_position'] = position
            print(f"encoder id{encoder['id']}: {position}")
            display.text(f"e{encoder['id']}: {position}")


def check_keyboard():
    while 1:
        event = km.events.get()
        if not event:
            break
        # print(event)
        print(f"{event.key_number} {event.pressed} {event.released} {event.timestamp} ")
        display.text(f"key {event.key_number+1} {event.pressed}")
        if event.pressed:
            r = random.randrange(0,256)
            g = random.randrange(0,256)
            b = random.randrange(0,256)
            i = l2b[event.key_number+1]
            pixels[i] = (r,g,b)


def calibrate_pots_limits():
    for pot in pots:
        pot['min'] = 65536
        pot['max'] = 0
    print_resoult = True
    while True:
        for pot in pots:
            sleep(0.05)
            value = pot['apin'].value
            if value < pot['min']:
                pot['min'] = value
                print_resoult=True
            elif value > pot['max']:
                pot['max'] = value
                print_resoult=True
        if print_resoult:
            s = ""
            for pot in pots:
                s+=f"id{pot['id']} min {pot['min']} max {pot['max']}, "
            print(s)
            print_resoult=False

def calibrate_pots_threshold():
    for pot in pots:
        pot['m'] = 0

    while True:
        s = ""
        for pot in pots:
            r = pot['apin'].value
            for i in range(50):
                sleep(0.005)
                v = pot['apin'].value
                if abs(v-r) > pot['m']:
                    pot['m']=abs(v-r)
            s+=f"{pot['id']}: {pot['m']}, "
        print(s)
        sleep(5)


pixels[0] = (0, 128, 0)  # status LED

# calibrate_pots_limits()
# calibrate_pots_threshold()
counter = 0
# try:
while True:
    check_pots()
    check_encoders()
    check_keyboard()
    if counter%5 == 0:
        display.update()
    counter+=1
    sleep(0.01)
    # except MemoryError:  # because of the display
# except:
#     pixels[0] = (128, 0, 0)
#     pixels.brightness = 0.25
# displayio.release_displays()
