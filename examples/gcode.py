import fidgetpy as fp
import math


ngcfile = "titan_1m_setup1.nc"


def square_endmill(diameter):
    p = fp.axes()
    return fp.revolve_z(fp.intersection(-p.z, p.x - diameter / 2))


def drill_bit(diameter, tip_angle):
    p = fp.axes()
    od = p.x - diameter / 2
    theta = math.radians(tip_angle) / 2 + math.radians(90)
    tip = p.xz.dot(fp.Vec2(math.sin(theta), math.cos(theta)))
    return fp.revolve_z(fp.intersection(od, tip))


def ball_endmill(diameter):
    p = fp.axes()
    return (p.length() - diameter / 2).remap_xyz(
        p.x, p.y, fp.min_(p.z - diameter / 2, 0)
    )


def bullnose_endmill(diameter, radius):
    if abs(diameter / 2 - radius) < 0.0001:
        return ball_endmill(diameter)
    p = fp.axes()
    r1 = p.xy.length() - (diameter / 2 - radius)
    torus = fp.Vec2(r1, p.z).length() - radius
    stretched_torus = torus.remap_xyz(p.x, p.y, fp.min_(p.z - radius, 0))
    inner_cylinder = square_endmill(diameter - 2 * radius)
    return fp.union(stretched_torus, inner_cylinder)


def linear_move(tool: fp.Tree, start: fp.Vec3, end: fp.Vec3) -> fp.Tree:
    p = fp.axes()
    # p =fp.Vec2(p.x-fp.clamp(p.x,0,0.05), p.y-fp.clamp(p.y,0,0.05), p.z)
    pa = p - start
    ba = end - start
    h = fp.clamp(pa.dot(ba) / ba.dot(ba), 0.0, 1.0)
    xp, yp, zp = pp = pa - ba * h
    return tool.remap_xyz(xp, yp, zp)
    # return fp.max_(pp.xy.length() - 0.1, -pp.z)


def arc_move(tool, start, end, relcenter, mode="G2"):
    r = relcenter.length()
    center = start + relcenter
    t1 = fp.atan2(*(start - center).yx)
    t2 = fp.atan2(*(end - center).yx)
    if mode == "G2":
        t = (t2 - t1) % math.tau
    elif mode == "G3":
        t = (math.tau + t1 - t2) % math.tau
    print(t)
    p = x, y, z = fp.axes()
    this_t = fp.atan2(y, x)
    new_t = fp.clamp(this_t, -t / 2, t / 2)
    d1 = fp.Vec2(r * fp.cos(new_t), r * fp.sin(new_t)) - p.xy
    r1 = tool.remap_xyz(d1.x, d1.y, z)
    r2 = r1.remap_xyz(
        x * math.cos(-t / 2) - y * math.sin(-t / 2),
        x * math.sin(-t / 2) + y * math.cos(-t / 2),
        z,
    )
    r3 = r2.remap_xyz(x + r, y, z)
    t2 = math.pi - fp.atan2(*relcenter.yx)
    r4 = r3.remap_xyz(
        x * math.cos(t2) - y * math.sin(t2), x * math.sin(t2) + y * math.cos(t2), z
    )
    return r4


""" tools.tbl
;
T4 P4 Z0.0 D0.250; 1/4" 90 degree spot drill
T5 P5 Z0.0 D1.4961 ; 38mm diameter face mill
T19 P19 Z0.0 D0.375; 3/8" square endmill
T121 P121 Z0.0 D0.159; #21 screw machine length drill
"""

tools = {
    4: drill_bit(0.250, 90.0),
    5: bullnose_endmill(38.0 / 25.4, 0.03),
    19: square_endmill(0.375),
    121: drill_bit(0.159, 135.0),
}


# machine state
pos = fp.Vec3(0, 0, 0)
tool = 0
operations = []

with open(ngcfile) as f:
    blocks = f.readlines()

for b in blocks:
    cmd = b[:2]
    if cmd in ("G0", "G1", "G2", "G3"):
        new_x, new_y, new_z = pos
        ival = jval = 0.0
        for axis in b[2:].split():
            match axis[0]:
                case "X":
                    new_x = float(axis[1:])
                case "Y":
                    new_y = float(axis[1:])
                case "Z":
                    new_z = float(axis[1:])
                case "I":
                    ival = float(axis[1:])
                case "J":
                    jval = float(axis[1:])
        newpos = fp.Vec3(new_x, new_y, new_z)
        arc_center = fp.Vec2(ival, jval)
    else:
        newpos = pos
        arc_center = None
    match cmd:
        case "G0":
            # print(f"moveto {newpos}")
            pass
        case "G1":
            # print(f"cutto {newpos}")
            pass
        case "G2":
            # print(f"ccw_arc {newpos}")
            rad = (pos.xy - arc_center).length()

        case "G3":
            # print(f"cw_arc {newpos}")
            pass
        case "M6":
            tool = int(b[4:])
            print(f"toolchange to T{tool}")
        case _:
            pass
    pos = newpos


tool = tools[19]
# shp = linear_move(tool, fp.Vec3(0,0,0), fp.Vec3(0.25,0.25,0))
shp = arc_move(tool, fp.Vec3(0, 0, 0), fp.Vec3(0, 0.5, 0), fp.Vec3(0, 0.5, 0), "G3")
print(shp.to_graphviz())
with open("./test.stl", "wb") as f:
    f.write(shp.mesh(6).to_stl())
