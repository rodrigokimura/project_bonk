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
