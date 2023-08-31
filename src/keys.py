import usb_hid
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.mouse import Mouse


def get_opts(cls: type[object]):
    return {
        k for k, v in cls.__dict__.items() if not k.startswith("_") and not callable(v)
    }


class KeyWrapper:
    sender_map = {
        Keyboard(usb_hid.devices): Keycode,
        Mouse(usb_hid.devices): Mouse,
        ConsumerControl(usb_hid.devices): ConsumerControlCode,
    }

    def __init__(self, keys: str | list[str]) -> None:
        if isinstance(keys, str):
            keys = [keys]

        self.key_sets = {
            sender: get_opts(contants) for sender, contants in self.sender_map.items()
        }
        self._sanity_check()
        self.press_commands = []
        self.release_commands = []
        self.key_codes = []
        self.senders = []
        for key in keys:
            key = key.upper()
            for sender, key_set in self.key_sets.items():
                if key in key_set:
                    key_code = getattr(self.sender_map[sender], key)
                    self.senders.append(sender)
                    self.key_codes.append(key_code)

    def _sanity_check(self):
        union_all = set()
        for s in self.key_sets.values():
            union_all |= s

        assert sum(len(s) for s in self.key_sets.values()) == len(
            union_all
        ), "Overlapping contanst names"

    def _press(self, sender, key_code):
        if isinstance(sender, ConsumerControl):
            sender.send(key_code)
        elif isinstance(sender, Keyboard):
            sender.press(key_code)
        elif isinstance(sender, Mouse):
            sender.click(key_code)

    def _release(self, sender, key_code):
        if isinstance(sender, ConsumerControl):
            pass
        elif isinstance(sender, Keyboard):
            sender.release(key_code)
        elif isinstance(sender, Mouse):
            pass

    def press(self):
        for sender, key_code in zip(self.senders, self.key_codes):
            self._press(sender, key_code)

    def release(self):
        for sender, key_code in zip(self.senders, self.key_codes):
            self._release(sender, key_code)

    def press_and_release(self):
        self.press()
        self.release()
