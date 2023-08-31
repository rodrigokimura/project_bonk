# import pyb
from time import sleep

from machine import Pin


def fast_blink():
    led = Pin(25, Pin.OUT)
    for _ in range(6):
        led.toggle()
        sleep(0.1)


if __name__ == "__main__":
    fast_blink()
