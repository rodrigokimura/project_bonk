import time

import analogio
import board
import digitalio
import neopixel
import rotaryio  # type: ignore
import usb_hid
from adafruit_hid.mouse import Mouse

from keys import KeyWrapper
from utils import load_config, parse_color

"""Pin mapping:
    clk: 13
    dt: 14
    sw: 15

    vry: 26
    vrx: 27
    gnd: agnd
    sw: 22
"""


class Knob:
    def __init__(self) -> None:
        self.led = digitalio.DigitalInOut(board.LED)  # type: ignore
        self.led.direction = digitalio.Direction.OUTPUT

        self.encoder_switch = digitalio.DigitalInOut(board.GP15)  # type: ignore
        self.encoder_switch.direction = digitalio.Direction.INPUT
        self.encoder_switch.pull = digitalio.Pull.UP
        self.encoder_switch_value = False

        self.stick_switch = digitalio.DigitalInOut(board.GP22)  # type: ignore
        self.stick_switch.direction = digitalio.Direction.INPUT
        self.stick_switch.pull = digitalio.Pull.UP
        self.stick_switch_value = False

        self.encoder = rotaryio.IncrementalEncoder(board.GP13, board.GP14, 4)  # type: ignore
        self.ay = analogio.AnalogIn(board.GP26)  # type: ignore
        self.ax = analogio.AnalogIn(board.GP27)  # type: ignore
        self.pixels = neopixel.NeoPixel(board.GP23, 1)  # type: ignore

        self.last_position = 0
        self.key_cw = KeyWrapper("volume_increment")
        self.key_ccw = KeyWrapper("volume_decrement")
        self.mouse = Mouse(usb_hid.devices)
        self.layer_index = 0

        config = load_config()
        self.layers = config.get("layers", [])
        self._load_layer()

    def run(self):
        while True:
            position = self.encoder.position
            if position != self.last_position:
                if self.last_position < position:
                    self.key_cw.press_and_release()
                    self.blink()
                if self.last_position > position:
                    self.key_ccw.press_and_release()
                    self.blink()
            self.last_position = position
            self.move_mouse()
            self.read_buttons()

    def read_buttons(self):
        if self.encoder_switch_value != self.encoder_switch.value:
            self.encoder_switch_value = self.encoder_switch.value
            if self.encoder_switch_value == False:  # pressed
                print("Encoder switch pressed")
                self.next_layer()
            else:
                print("Encoder switch released")

        if self.stick_switch_value != self.stick_switch.value:
            self.stick_switch_value = self.stick_switch.value
            if self.stick_switch_value == False:  # pressed
                print("Stick switch pressed")
                self.initial_layer()
            else:
                print("Stick switch released")

    def next_layer(self):
        if self.layer_index == len(self.layers) - 1:
            self.layer_index = 0
        else:
            self.layer_index += 1
        self._load_layer()

    def initial_layer(self):
        self.layer_index = 0
        self._load_layer()

    def _load_layer(self):
        layer = self.layers[self.layer_index]
        self.pixels[0] = parse_color(layer.get("color", "#000000"))
        self.key_cw = layer.get("encoder", {}).get("cw", "")
        self.key_ccw = layer.get("encoder", {}).get("ccw", "")
        print(f"Active layer: {layer.get('name', 'untitled')}")

    def get_stick_position(self):
        x, y = self.ax.value, self.ay.value
        x //= 256
        y //= 256
        x -= 256 / 2
        y -= 256 / 2
        tolerance = 100
        if abs(x) < tolerance and abs(y) < tolerance:
            return None
        return x, y

    def move_mouse(self):
        position = self.get_stick_position()
        if position:
            x, y = position
            self.mouse.move(int(x / 20), int(y / 20))

    def blink(self):
        self.led.value = not self.led.value
        time.sleep(0.1)
        self.led.value = not self.led.value


if __name__ == "__main__":
    knob = Knob()
    knob.run()
