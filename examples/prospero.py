from fidgetpy import Vec2, axes, axes2d, min_, max_, Tree, cut


prospero = """But this rough magic I
here abjure, and when
I have required some
heavenly music, which even
now I do, to work mine
end upon their senses that
this airy charm is for, I'll
break my staff, bury it
certain fathoms in the
earth, and deeper than did
ever plummet sound
I'll drown my book."""

# set(prospero) == {'g', 'o', 'p', 'b', 'a', 'n', 'j', 'u', ' ', 'w', 'B', 'm', 'h', 'q', 'y', 'I', 'e', 't', 'r', '.', '\n', 'v', 's', 'd', "'", 'f', 'c', 'i', 'l', 'k', ','}
# len(set(prospero)) == 29


def move(part, dx, dy, dz=0):
    x, y, z = axes()
    if dx == 0:
        new_x = x
    else:
        new_x = x - dx
    if dy == 0:
        new_y = y
    else:
        new_y = y - dy
    if dz == 0:
        new_z = z
    else:
        new_z = z - dz
    return part.remap_xyz(new_x, new_y, new_z)


def scale_xy(part, x0, y0, sx, sy=None):
    if sy is None:
        sy = sx
    x, y, z = axes()
    if x0 == 0:
        xp = x / sx
    else:
        xp = x0 + (x - x0) / sx
    if y0 == 0:
        yp = y / sy
    else:
        yp = y0 + (y - y0) / sy
    return part.remap_xyz(xp, yp, z)


def scale_y(part, y0, sy):
    x, y, z = axes()
    yp = y0 + (y - y0) / sy
    return part.remap_xyz(x, yp, z)


def shear_x_y(part, ymin, ymax, dx0, dx1):
    x, y, z = axes()
    dx = dx1 - dx0
    dy = ymax - ymin
    xp = x - dx0 - dx * (y - ymin) / dy
    return part.remap_xyz(xp, y, z)


def text(text, x, y, height=1, align="LB", lineheight=1.55):
    if text == "":
        raise RuntimeError("Empty string supplied to text() function")
    dx, dy = 0, -1
    text_shape = None

    for line in text.split("\n"):
        line_shape = None

        for c in line:
            if c not in _glyphs.keys():
                raise RuntimeError('Unknown character "%s"' % c)
            else:
                if c != " ":
                    chr_math = move(_glyphs[c], dx, dy)
                    if line_shape is None:
                        line_shape = chr_math
                    else:
                        line_shape |= chr_math
                dx += _widths[c] + 0.1
        dx -= 0.1

        if line_shape is not None:
            if align[0] == "L":
                pass
            elif align[0] == "C":
                line_shape = move(line_shape, -dx / 2, 0)
            elif align[0] == "R":
                line_shape = move(line_shape, -dx, 0)

            if text_shape is None:
                text_shape = line_shape
            else:
                text_shape |= line_shape

        dy -= lineheight
        dx = 0
    dy += lineheight
    if text_shape is None:
        return None

    if align[1] == "T":
        pass
    elif align[1] == "B":
        text_shape = move(
            text_shape,
            0,
            -dy,
        )
    elif align[1] == "C":
        text_shape = move(text_shape, 0, -dy / 2)

    if height != 1:
        text_shape = scale_xy(text_shape, 0, 0, height)

    return move(text_shape, x, y)


def box(xmin, xmax, ymin, ymax):
    x, y = axes2d()
    xc = round((xmax + xmin) / 2, 3)
    yc = round((ymax + ymin) / 2, 3)
    xhlen = round(abs(xmax - xmin) / 2, 3)
    yhlen = round(abs(ymax - ymin) / 2, 3)
    cx, cy = Vec2(x - xc, y - yc)
    s = max_(abs(cx) - xhlen, abs(cy) - yhlen)
    return s


def circle(xc, yc, rad, fill):
    x, y = axes2d()
    p = ax, ay = Vec2(x - xc, y - yc)
    if fill:
        return p.length() - rad
    return abs(p.length() - rad)


def scale_x(part, x0, sx):
    x, y, z = axes()
    if x0:
        xp = x0 + (x - x0) / sx
    else:
        xp = x / sx
    return part.remap_xyz(xp, y, z)


def glyph_w():
    # build our own w
    x, y = axes2d()
    x = x - 0.4
    x = abs(x)
    p = Vec2(x, y)
    bottom = -y
    top = y - 0.55
    mid_top = y - 0.5
    side = (p - Vec2(0.25, 0)).dot(Vec2(0.96, -0.26))
    bottom_cutout = (p - Vec2(0, 0.375)).dot(Vec2(-0.93, -0.37))
    uc1 = -side - 0.096
    uc2 = -bottom_cutout - 0.093

    s = max_(
        min_(max_(max_(uc2, bottom_cutout), mid_top), max_(side, uc1)),
        max_(top, bottom),
    )
    return s


def glyph_y():
    x, y = axes2d()
    # x = x - 0.4
    # x = abs(x)
    p = Vec2(x, y)
    _1 = (Vec2(x, abs(y)) - Vec2(0.225, 0)).dot(Vec2(-0.93, -0.38))
    _2 = (p - Vec2(0.325, 0)).dot(Vec2(0.93, -0.38))
    _3 = _2 + 0.093
    _4 = _1 + 0.093
    _5 = max_(_1, _2)
    _6 = max_(_3, _4)
    _7 = cut(_5, _6)
    _8 = y - 0.55
    _9 = -0.375 - y
    _10 = max_(_8, _9)
    s = max_(_7, _10)
    return s


def glyph_c():
    x, y = axes2d()
    p = ax, ay = Vec2(x - 0.275, y - 0.275)
    _1 = abs(p.length() - 0.225)
    _2 = _1 - 0.05
    _3 = Vec2(ax, abs(ay)).dot(Vec2(0.71, -0.71))
    s = max_(_3, _2)
    return s


def glyph_o():
    _1 = circle(0.275, 0.275, 0.225, False)
    s = _1 - 0.05
    return s


def glyph_l():
    return box(0.025, 0.125, 0.0, 1.0)


def glyph_h():
    x, y = axes2d()
    xc = x - 0.275
    yc = y - 0.275
    p = Vec2(xc, max_(yc, 0.0))
    _1 = abs(p.length() - 0.225)
    _2 = _1 - 0.05
    _3 = max_(_2, -y)
    return min_(box(0, 0.1, 0, 1), _3)


def glyph_n():
    x, y = axes2d()
    xc = x - 0.275
    yc = y - 0.275
    p = Vec2(xc, max_(yc, 0.0))
    _1 = abs(p.length() - 0.225)
    _2 = _1 - 0.05
    _3 = max_(_2, -y)
    return min_(box(0, 0.1, 0, 0.55), _3)


def glyph_j():
    x, y = axes2d()
    xc = x
    yc = y + 0.1
    p = Vec2(xc, min_(yc, 0.0))
    _1 = abs(p.length() - 0.225) - 0.05
    _2 = max_(_1, -x)
    _3 = max_(_2, y - 0.55)
    s = min_(_3, circle(0.225, 0.7, 0.075, True))
    return s


def glyph_u():
    x, y = axes2d()
    xc = x - 0.275
    yc = y - 0.275
    p = Vec2(xc, min_(yc, 0.0))
    _1 = abs(p.length() - 0.225)
    _2 = _1 - 0.05
    _3 = max_(_2, y - 0.55)
    _4 = box(0.45, 0.55, 0, 0.55)
    return min_(_3, _4)


def glyph_B():
    x, y, z = axes()
    xc = x - 0.3
    yc = y - 0.275
    p = Vec2(max_(xc, 0.0), yc)
    _1 = abs(p.length() - 0.225)
    _2 = _1 - 0.05
    _3 = max_(_2, 0.05 - x)
    _4 = _3.remap_xyz(x, abs(y - 0.5) + 0.05, z)
    _5 = min_(_4, box(0, 0.1, 0, 1))
    return _5


def glyph_m():
    x, y, z = axes()
    xc = x - 0.175
    yc = y - 0.35
    p = Vec2(xc, max_(yc, 0))
    s = abs(p.length() - 0.125)
    s = s - 0.05
    s = max_(s, -y)
    s = s.remap_xyz(abs(x - 0.3) + 0.05, y, z)
    s = min_(s, box(0, 0.1, 0, 0.525))
    return s


def glyph_q():
    s = circle(0.275, 0.275, 0.225, False) - 0.05
    s = min_(s, box(0.45, 0.55, -0.375, 0.55))
    return s


def glyph_I():
    s = box(0, 0.5, 0, 0.1)
    s = min_(s, box(0, 0.5, 0.9, 1))
    s = min_(s, box(0.2, 0.3, 0.05, 0.95))
    return s


def glyph_e():
    x, y = p = axes2d()
    s = -circle(0.275, 0.275, 0.175, True)
    plane1 = -0.275 + y
    plane2 = (p - Vec2(0.6, 0)).dot(Vec2(-0.482, -0.876))
    s = max_(s, -max_(plane1, plane2))
    s = min_(s, abs(y - 0.27) - 0.045)
    s = max_(s, circle(0.275, 0.275, 0.275, True))
    return s


def glyph_t():
    x, y = axes2d()
    p = Vec2(x - 0.4, min_(y - 0.25, 0.0))
    s = abs(p.length() - 0.2) - 0.05
    s = max_(s, y - 1)
    s = max_(s, x - 0.4)
    s = min_(s, box(0, 0.4, 0.55, 0.65))
    return s


def glyph_r():
    x, y = axes2d()
    shape = circle(0.55, 0, 0.55, True) & ~scale_x(
        circle(0.55, 0, 0.45, True), 0.55, 0.8
    )
    shape &= -y
    shape &= x - 0.55
    shape = scale_x(shape, 0, 0.7)
    shape |= box(0, 0.1, 0, 0.55)
    return shape


def glyph_period():
    return circle(0.075, 0.075, 0.075, True)


def glyph_v():
    x, y = axes2d()
    x = x - 0.3
    x = abs(x)
    p = Vec2(x, y)
    s = (p - Vec2(-0.05, 0)).dot(Vec2(-0.91, 0.414))
    s = max_(s, -s - 0.091)
    s = max_(s, -y)
    s = max_(s, -0.55 + y)
    return s


def glyph_s():
    x, y, z = axes()
    y - 0.39
    xc = 0.2435
    s = circle(0, 0, 0.1625, True)
    s = max_(s, -circle(0, 0, 0.0625, True).remap_xyz(x / 1.5, y, z))
    s = max_(s, -max_(-x, y))
    s = s.remap_xyz(x / 1.5, y, z)
    upper = s.remap_xyz(x - xc, y - 0.3875, z)
    lower = s.remap_xyz(-x + xc, -y + 0.1625, z)
    return min_(upper, lower)


def glyph_d():
    x, y = axes2d()
    xc = x - 0.275
    yc = y - 0.275
    p = Vec2(min_(xc, 0.0), yc)
    s = abs(p.length() - 0.225) - 0.05
    s = max_(s, x - 0.475)
    s = min_(s, box(0.425, 0.525, 0, 1))
    return s


def glyph_b():
    x, y = axes2d()
    xc = x - 0.25
    yc = y - 0.275
    p = Vec2(max_(xc, 0.0), yc)
    s = abs(p.length() - 0.225) - 0.05
    s = max_(s, 0.05 - x)
    s = min_(s, box(0, 0.1, 0, 1))
    return s


def glyph_singlequote():
    return box(0, 0.1, 0.55, 0.8)


def glyph_i():
    return min_(box(0.025, 0.125, 0, 0.55), circle(0.075, 0.7, 0.075, True))


def glyph_f():
    x, y = axes2d()
    xc = x - 0.4
    yc = y - 0.75
    p = Vec2(xc, max_(yc, 0.0))
    s = abs(p.length() - 0.2) - 0.05
    s = max_(s, xc)
    s = max_(s, -y)
    s = min_(s, box(0, 0.4, 0.45, 0.55))
    return s


def glyph_k():
    x, y = p = axes2d()
    p1 = -x
    p2 = -p1 - 0.1
    p3 = -y
    p4 = -p3 - 1.0
    p5 = (p - Vec2(0, 1.1)).dot(Vec2(0.707, 0.707))
    p6 = -(p - Vec2(0.36, 0)).dot(Vec2(0.693, 0.721))
    p7 = -p6 - 0.1
    p8 = (p - Vec2(0, 0.313)).dot(Vec2(-0.809, 0.589))
    p9 = -p8 - 0.1
    s = max_(p3, p4)
    s = max_(s, p1)
    s = max_(s, p5)
    s = max_(s, min_(p2, p6))
    s = max_(s, min_(p2, p8))
    s = max_(s, min_(p9, p7))
    return s


def glyph_g():
    x, y = axes2d()
    xc = x - 0.275
    yc = y + 0.1
    p = Vec2(xc, min_(yc, 0.0))
    s = abs(p.length() - 0.225) - 0.05
    s = max_(s, min_(-xc, yc))
    s = max_(s, y - 0.55)
    s = min_(s, circle(0.275, 0.275, 0.225, False) - 0.05)
    return s


def glyph_a():
    shape = circle(0.25, 0.275, 0.225, False) - 0.05
    shape = shear_x_y(shape, 0, 0.35, 0, 0.1)
    shape |= box(0.51, 0.61, 0, 0.35)
    shape = move(shape, -0.05, 0)
    return shape


def glyph_comma():
    shape = glyph_period()
    return shape


def glyph_p():
    s = circle(0.275, 0.275, 0.225, False) - 0.05
    s = min_(s, box(0, 0.1, -0.375, 0.55))
    return s


_glyphs = {
    ".": glyph_period(),
    "'": glyph_singlequote(),
    "B": glyph_B(),
    "c": glyph_c(),
    "d": glyph_d(),
    "f": glyph_f(),
    "h": glyph_h(),
    "i": glyph_i(),
    "I": glyph_I(),
    "j": glyph_j(),
    "k": glyph_k(),
    "l": glyph_l(),
    "m": glyph_m(),
    "n": glyph_n(),
    "o": glyph_o(),
    "q": glyph_q(),
    "s": glyph_s(),
    "t": glyph_t(),
    "u": glyph_u(),
    "v": glyph_v(),
    "w": glyph_w(),
    "y": glyph_y(),
    " ": None,
    "r": glyph_r(),
    "g": glyph_g(),
    "a": glyph_a(),
    "e": glyph_e(),
    "b": glyph_b(),
    ",": glyph_comma(),
    "p": glyph_p(),
}

_widths = {
    ".": 0.15,
    "'": 0.1,
    "B": 0.575,
    "c": 0.48,
    "d": 0.525,
    "f": 0.4,
    "h": 0.55,
    "i": 0.15,
    "I": 0.5,
    "j": 0.3,
    "k": 0.5,
    "l": 0.15,
    "m": 0.6,
    "n": 0.55,
    "o": 0.55,
    "q": 0.55,
    "s": 0.4875,
    "t": 0.4,
    "u": 0.55,
    "v": 0.6,
    "w": 0.8,
    "y": 0.55,
    " ": 0.55,
    "r": 0.385,
    "g": 0.55,
    "a": 0.58,
    "e": 0.55,
    "b": 0.525,
    ",": 0.175,
    "p": 0.55,
}

if __name__ == "__main__":
    x, y, z = axes()
    sf = 8
    s1 = text(prospero, 0, 0, 1, "CC", 1.15).remap_xyz(x * sf, y * sf, z)
    with open("/home/alex/Code/fidget/models/prospero.vm") as f:
        dat = f.read()
    s2 = Tree.from_vm(dat)
    s = min_(s1, s2)
    s = s1
    # r = s.to_rhai()
    print(f"writing shape with {len(s)} expressions")
    # with open("/home/alex/prospero_optimized.rhai", 'w') as f:
    #     f.write(r)
    with open("/home/alex/prospero_optimized.vm", "w") as f:
        f.write(s.to_vm())
