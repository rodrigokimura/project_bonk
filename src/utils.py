import json
import math

from keys import KeyWrapper


def parse_color(color: str | list[int]) -> tuple[int, int, int]:
    if isinstance(color, str):
        if color[0] == "#":
            color = color[1:]
        if len(color) != 6:
            raise ValueError("Invalid color")
        r = color[:2]
        g = color[2:4]
        b = color[4:]
        return int(r, 16), int(g, 16), int(b, 16)

    if isinstance(color, list):
        r = color[0]
        g = color[1]
        b = color[2]
        return int(r), int(g), int(b)

    raise NotImplementedError


def load_config():
    with open("config.json") as file:
        config = json.load(file)
    layers = config.get("layers", [])
    for layer in layers:
        cw = layer.get("encoder", {}).get("cw")
        layer["encoder"]["cw"] = KeyWrapper(cw)

        ccw = layer.get("encoder", {}).get("ccw")
        layer["encoder"]["ccw"] = KeyWrapper(ccw)

        stick = layer.get("stick", {})
        if stick.get("mode") == "dpad":
            for d in ("up", "down", "left", "right"):
                stick[d] = KeyWrapper(stick.get(d))
    return config


def position_to_direction(position: tuple[int | float, int | float] | None):
    if position is None:
        return None
    x, y = position
    angle = math.atan2(y, x)
    angle += math.pi  # zero is left, rotates cw
    angle /= math.pi / 2
    if 0.5 < angle < 1.5:
        return "up"
    if 1.5 < angle < 2.5:
        return "right"
    if 2.5 < angle < 3.5:
        return "down"
    return "left"
