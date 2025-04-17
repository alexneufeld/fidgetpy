import os
from xml.dom import minidom
from fidgetpy.types import Tree, Vec2
from fidgetpy.math import clamp, axes, min_, max_
from typing import Self
import functools


def multiunion(*args):
    return functools.reduce(min_, args)


def extrude_z(tree, height):
    z = Tree.z()
    return max_(max_(-z, z - height), tree)


def linesegment(a: Vec2, b: Vec2) -> Tree:
    x, y, _ = axes()
    p = Vec2(x, y)
    ba = b - a
    pa = p - a
    h = clamp(pa.dot(ba) / ba.dot(ba), 0.0, 1.0)
    return (pa - ba * h).length()


FONT_DIR = os.path.join(os.path.dirname(__file__), "svg_fonts")


def parse_d(d: str) -> list[str]:
    items = []
    state = None
    i = iter(d)
    while (c := next(i, None)) is not None:
        if c == " ":
            state = None
            continue
        elif c in "0123456789.+-e":
            if state == "number":
                items[-1] += c
            else:
                items.append(c)
            state = "number"
        elif c.isalpha():
            # all commands are single letters
            state = None
            items.append(c)
    return items


class HersheyFont:
    def __init__(self):
        pass

    def render_string(self, s: str, em_height=1.0, stroke_width=0.05) -> Tree:
        x = 0.0
        charshapes = []
        for c in s:
            nodes, advance = self.glyphs[c]
            strokes = [x - stroke_width for x in nodes]
            x0, y0, z0 = axes()
            charshapes.append(multiunion(*strokes).remap_xyz(x0 - x, y0, z0))
            x += advance
        sf = self.fdata["units-per-em"] / em_height
        return multiunion(*charshapes).remap_xyz(*(axes() * sf))

    @staticmethod
    def from_file(fpath, ingest_scale_factor=1 / 1000) -> Self:
        doc = minidom.parse(fpath)
        font_attrs = doc.getElementsByTagName("font-face")[0]
        fdata = {
            "font-family": font_attrs.getAttribute("font-family"),
            "units-per-em": float(font_attrs.getAttribute("units-per-em"))
            * ingest_scale_factor,
            "ascent": float(font_attrs.getAttribute("ascent")) * ingest_scale_factor,
            "descent": float(font_attrs.getAttribute("descent")) * ingest_scale_factor,
            "cap-height": float(font_attrs.getAttribute("cap-height"))
            * ingest_scale_factor,
            "x-height": float(font_attrs.getAttribute("x-height"))
            * ingest_scale_factor,
            "default-advance": float(
                doc.getElementsByTagName("font")[0].getAttribute("horiz-adv-x")
            )
            * ingest_scale_factor,
        }

        charmap = dict()

        for glyph in doc.getElementsByTagName("glyph"):
            uc = glyph.getAttribute("unicode")
            paths = []
            advance = float(glyph.getAttribute("horiz-adv-x")) * ingest_scale_factor
            current_pos = Vec2(0, 0)
            gd = glyph.getAttribute("d")
            items = parse_d(gd)
            i = iter(items)
            while (cmd := next(i, None)) is not None:
                # Note: Commands are case-sensitive.
                # An upper-case command specifies absolute coordinates,
                # while a lower-case command specifies coordinates relative
                # to the current position.
                # ref: https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/d
                match cmd:
                    case "M":
                        new_x = next(i, None)
                        new_y = next(i, None)
                        if (not new_y) or (not new_y):
                            errmsg = "Ran out of d items while parsing M command"
                            raise RuntimeError()
                        current_pos = Vec2(float(new_x), float(new_y))
                    case "L":
                        new_x = next(i, None)
                        new_y = next(i, None)
                        if (not new_y) or (not new_y):
                            errmsg = "Ran out of d items while parsing L command"
                            raise RuntimeError(errmsg)
                        new_pos = Vec2(float(new_x), float(new_y))
                        paths.append(
                            linesegment(
                                Vec2(
                                    current_pos.x * ingest_scale_factor,
                                    current_pos.y * ingest_scale_factor,
                                ),
                                Vec2(
                                    new_pos.x * ingest_scale_factor,
                                    new_pos.y * ingest_scale_factor,
                                ),
                            )
                        )
                        current_pos = new_pos
                    case "C":
                        x1 = next(i, None)
                        y1 = next(i, None)
                        x2 = next(i, None)
                        y2 = next(i, None)
                        new_x = next(i, None)
                        new_y = next(i, None)
                        if (
                            (not x1)
                            or (not y1)
                            or (not x2)
                            or (not y2)
                            or (not new_x)
                            or (not new_y)
                        ):
                            errmsg = "Ran out of d items while parsing C command"
                            raise RuntimeError(errmsg)
                        # print("skipping cubic bezier")
                        new_pos = Vec2(float(new_x), float(new_y))
                        current_pos = new_pos
                    case "Z":
                        pass  # this is incorrect
                    case _:
                        print(items)
                        errmsg = f"failed to parse {gd}"
                        raise RuntimeError(errmsg)
            charmap[uc] = (paths, advance)
        instance = HersheyFont()
        instance.fdata = fdata
        instance.glyphs = charmap
        return instance


if __name__ == "__main__":
    HersheyGothEnglish = HersheyFont.from_file(
        os.path.join(FONT_DIR, "HersheyGothEnglish.svg")
    )
    p = axes()
    shp = extrude_z(HersheyGothEnglish.render_string("Hello!", 0.7, 0.01), 0.1)
    shp = shp.remap_xyz(p.x + 1.0, p.y + 0.2, p.z)
    outfile = os.path.join(os.path.dirname(__file__), "out/svg_font_test.stl")
    os.makedirs(os.path.dirname(outfile), exist_ok=True)
    with open(outfile, "wb") as f:
        f.write(shp.mesh(8, 0, 0, 0, 1).to_stl())
