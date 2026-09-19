from PIL import Image, ImageChops, ImageDraw, ImageOps

from utils import blend, hex_to_rgb

SS = 4  # supersampling factor
LANCZOS = Image.Resampling.LANCZOS


def _rgba(color, alpha=255):
    if isinstance(color, str):
        color = hex_to_rgb(color)
    return (color[0], color[1], color[2], alpha)


# --- Photos ------------------------------------------------------------
def round_corners(image, radius):
    image = image.convert("RGBA")
    width, height = image.size

    mask = Image.new("L", (width * SS, height * SS), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, width * SS - 1, height * SS - 1),
        radius=radius * SS,
        fill=255,
    )
    mask = mask.resize((width, height), LANCZOS)

    image.putalpha(ImageChops.multiply(image.getchannel("A"), mask))
    return image


def cover_image(source, size, radius):

    square = ImageOps.fit(source.convert("RGB"), (size, size), LANCZOS)
    return round_corners(square, radius)


def average_color(image):
    tiny = image.convert("RGB").resize((1, 1), Image.Resampling.BOX)
    return tiny.getpixel((0, 0))


def accent_from_color(rgb):

    strongest = max(rgb) or 1
    target = min(max(strongest, 90), 170)
    scale = target / strongest
    return tuple(int(channel * scale) for channel in rgb)


def diagonal_gradient(size, color_a, color_b):
    image = Image.new("RGB", (size, size))
    pixels = image.load()
    total = (size - 1) * 2 or 1

    for y in range(size):
        for x in range(size):
            pixels[x, y] = blend(color_a, color_b, (x + y) / total)

    return image


# --- Icon glyphs -------------------------------------------------------
def _stroke(draw, start, end, width, fill):
    draw.line([start, end], fill=fill, width=max(1, int(round(width))))
    radius = width / 2
    for x, y in (start, end):
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=fill)


def draw_glyph(draw, name, x, y, s, fill):

    def P(u, v):
        return (x + u * s, y + v * s)

    def box(u0, v0, u1, v1):
        return [P(min(u0, u1), min(v0, v1)), P(max(u0, u1), max(v0, v1))]

    if name == "play":
        draw.polygon([P(.30, .18), P(.30, .82), P(.82, .50)], fill=fill)

    elif name == "pause":
        for u0, u1 in ((.28, .42), (.58, .72)):
            draw.rounded_rectangle(box(u0, .20, u1, .80), radius=.04 * s, fill=fill)

    elif name == "stop":
        draw.rounded_rectangle(box(.26, .26, .74, .74), radius=.05 * s, fill=fill)

    elif name in ("prev", "next"):
        def U(u):
            return 1 - u if name == "next" else u

        draw.rectangle(box(U(.20), .22, U(.29), .78), fill=fill)
        draw.polygon([P(U(.80), .22), P(U(.80), .78), P(U(.33), .50)], fill=fill)

    elif name in ("volume", "volume_mute"):
        draw.polygon(
            [P(.12, .38), P(.30, .38), P(.50, .20), P(.50, .80), P(.30, .62), P(.12, .62)],
            fill=fill,
        )
        if name == "volume":
            for radius in (.20, .34):
                draw.arc(
                    [P(.5 - radius, .5 - radius), P(.5 + radius, .5 + radius)],
                    start=-50, end=50, fill=fill, width=max(1, int(.07 * s)),
                )
        else:
            _stroke(draw, P(.64, .38), P(.88, .62), .07 * s, fill)
            _stroke(draw, P(.88, .38), P(.64, .62), .07 * s, fill)

    elif name == "plus":
        _stroke(draw, P(.50, .22), P(.50, .78), .08 * s, fill)
        _stroke(draw, P(.22, .50), P(.78, .50), .08 * s, fill)

    elif name == "trash":
        _stroke(draw, P(.20, .32), P(.80, .32), .07 * s, fill)
        draw.rounded_rectangle(
            box(.40, .16, .60, .32), radius=.03 * s, outline=fill, width=max(1, int(.05 * s))
        )
        corners = [P(.28, .40), P(.72, .40), P(.67, .84), P(.33, .84)]
        for start, end in zip(corners, corners[1:] + corners[:1]):
            if start == corners[0] and end == corners[1]:
                continue  # the lid already covers the top edge
            _stroke(draw, start, end, .06 * s, fill)

    elif name == "bars":  # little equaliser shown next to the playing song
        for u0, u1, v0 in ((.20, .34, .48), (.43, .57, .20), (.66, .80, .60)):
            draw.rounded_rectangle(box(u0, v0, u1, .84), radius=.02 * s, fill=fill)

    elif name == "note":  # two beamed eighth notes
        draw.ellipse(box(.19, .635, .41, .805), fill=fill)
        draw.ellipse(box(.57, .555, .79, .725), fill=fill)
        draw.rectangle(box(.375, .22, .415, .72), fill=fill)
        draw.rectangle(box(.755, .14, .795, .64), fill=fill)
        draw.polygon([P(.375, .22), P(.795, .14), P(.795, .28), P(.375, .36)], fill=fill)

    else:
        raise ValueError(f"Unknown icon: {name}")


def draw_icon(name, size, color):
    big = size * SS
    image = Image.new("RGBA", (big, big), _rgba(color, 0))
    draw_glyph(ImageDraw.Draw(image), name, 0, 0, big, _rgba(color))
    return image.resize((size, size), LANCZOS)


def circle_image(glyph, size, fill, glyph_color, scale=0.62):
    big = size * SS
    image = Image.new("RGBA", (big, big), _rgba(fill, 0))
    draw = ImageDraw.Draw(image)
    draw.ellipse((0, 0, big - 1, big - 1), fill=_rgba(fill))

    glyph_size = big * scale
    offset = (big - glyph_size) / 2
    draw_glyph(draw, glyph, offset, offset, glyph_size, _rgba(glyph_color))

    return image.resize((size, size), LANCZOS)


def pill_image(width, height, fill=None, border=None, border_width=1):
    big_w, big_h = width * SS, height * SS
    image = Image.new("RGBA", (big_w, big_h), (0, 0, 0, 0))

    ImageDraw.Draw(image).rounded_rectangle(
        (0, 0, big_w - 1, big_h - 1),
        radius=big_h / 2,
        fill=_rgba(fill) if fill else None,
        outline=_rgba(border) if border else None,
        width=border_width * SS,
    )
    return image.resize((width, height), LANCZOS)


def placeholder_image(size, radius, background, glyph_color):
    big = size * SS
    image = Image.new("RGBA", (big, big), _rgba(background, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle(
        (0, 0, big - 1, big - 1), radius=radius * SS, fill=_rgba(background)
    )

    glyph_size = big * 0.5
    offset = (big - glyph_size) / 2
    draw_glyph(draw, "note", offset, offset, glyph_size, _rgba(glyph_color))

    return image.resize((size, size), LANCZOS)


def tile_image(size, radius, color_a, color_b):
    tile = round_corners(diagonal_gradient(size, color_a, color_b), radius)

    note_size = int(size * 0.58)
    note = draw_icon("note", note_size, "#FFFFFF")
    offset = (size - note_size) // 2
    tile.alpha_composite(note, (offset, offset))

    return tile