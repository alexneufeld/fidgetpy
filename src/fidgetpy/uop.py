from fidgetpy._core import Tree
from .vec import Vec2, axes
from .vmath import min_, max_
from numbers import Real

eps = 1e-10

def extrude_z(t: Tree, height: Real) -> Tree:
    x, y, z = axes()
    w = vec2(t, abs(z) - height/2)
    return (min_(max_(w.x, w.y), eps) + max_(w, eps).length()).remap_xyz(x, y, z-height/2)


def revolve_z(t: Tree) -> Tree:
    p = axes()
    return t.remap_xyz(p.xy.length(), p.y, p.z)
