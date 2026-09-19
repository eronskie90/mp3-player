def format_time(seconds):
    
    seconds = int(seconds)
    minutes, seconds = divmod(seconds, 60)
    return f"{minutes:02d}:{seconds:02d}"


def format_size(num_bytes):
    
    if num_bytes < 1024:
        return f"{num_bytes} B"

    size = float(num_bytes)
    for unit in ("KB", "MB", "GB"):
        size /= 1024
        if size < 1024 or unit == "GB":
            return f"{size:.1f} {unit}"


def hex_to_rgb(color):
    """'#1DB954' -> (29, 185, 84)"""
    color = color.lstrip("#")
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    """(29, 185, 84) -> '#1db954'"""
    return "#{:02x}{:02x}{:02x}".format(*(int(c) for c in rgb[:3]))


def blend(color_a, color_b, amount):
    
    return tuple(
        int(round(a + (b - a) * amount))
        for a, b in zip(color_a[:3], color_b[:3])
    )