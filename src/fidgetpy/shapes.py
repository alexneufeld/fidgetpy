import math
from numbers import Real
from fidgetpy._core import Tree
from .vec import Vec2, Vec3, axes, axes2d
from .vmath import max_, min_
from dataclasses import dataclass

inf = float("inf")


class ShapeBoundsWarning(RuntimeWarning):
    """Warn the user when a shape with a non-finite
    or otherwise messed up bounding box is rendered"""


@dataclass(frozen=True)
class BoundBox:
    xmin: Real
    xmax: Real
    ymin: Real
    ymax: Real
    zmin: Real
    zmax: Real

    @property
    def xlength(self) -> Real:
        return self.xmax - self.xmin

    @property
    def ylength(self) -> Real:
        return self.ymax - self.ymin

    @property
    def zlength(self) -> Real:
        return self.zmax - self.zmin

    @property
    def center(self) -> Vec3:
        return (
            Vec3(self.xmin, self.ymin, self.zmin)
            + Vec3(self.xmax, self.ymax, self.zmax)
        ) / 2

    @property
    def diagonal_length(self) -> Real:
        return (
            Vec3(self.xmax, self.ymax, self.zmax)
            - Vec3(self.xmin, self.ymin, self.zmin)
        ).length()


@dataclass(frozen=True)
class Shape:
    tree: Tree
    bounds: BoundBox

    def eval(self, x, y, z):
        return self.tree.eval(x, y, z)

    def mesh(self, depth):
        # return self.tree.mesh(depth)
        # create an adjusted bounding box to compensate for infinite shapes
        bb = BoundBox(
            self.bounds.xmin if math.isfinite(self.bounds.xmin) else -1.0,
            self.bounds.xmax if math.isfinite(self.bounds.xmax) else 1.0,
            self.bounds.ymin if math.isfinite(self.bounds.ymin) else -1.0,
            self.bounds.ymax if math.isfinite(self.bounds.ymax) else 1.0,
            self.bounds.zmin if math.isfinite(self.bounds.zmin) else -1.0,
            self.bounds.zmax if math.isfinite(self.bounds.zmax) else 1.0,
        )
        if bb != self.bounds:
            raise ShapeBoundsWarning(
                "Shape has at least one non-finite bounding box face, "
                "mesh output may be truncated."
                f" Original bounding box: {self.bounds}"
            )
        # rescale the shape so that it fits inside a bounding box of [-1, 1] on all axis
        sf = 1.01 * max(bb.xlength, bb.ylength, bb.zlength)
        mesh = self.tree.mesh(depth, *bb.center, sf)
        return mesh


def sphere(r) -> Shape:
    """
    A sphere with radius r, centerered at the origin.

    Exact distance field.
    """
    return Shape(axes().length() - r, BoundBox(-r, r, -r, r, -r, r))


def circle(r) -> Shape:
    return Shape(axes2d().length() - r, BoundBox(-r, r, -r, r, -inf, inf))


def box(lx, ly, lz) -> Shape:
    """
    A rectangular box, centered at the origin.

    Exact distance field.
    """
    eps = min(lx, ly, lz) * 1e-6
    p = axes()
    q = abs(p) - Vec3(lx, ly, lz) / 2
    df = (max_(q, eps)).length() + min_(max_(q.x, max_(q.y, q.z)), eps)
    bb = BoundBox(-lx, lx, -ly, ly, -lz, lz)
    return Shape(df, bb)


def rectangle(lx, ly) -> Shape:
    eps = min(lx, ly) * 1e-6
    p = axes()
    q = abs(p) - Vec2(lx, ly) / 2
    df = (max_(q, eps)).length() + min_(max_(q.x, max_(q.y, q.z)), eps)
    bb = BoundBox(-lx, lx, -ly, ly, -inf, inf)
    return Shape(df, bb)


def torus(major_radius, minor_radius) -> Shape:
    """
    A torus, centered at the origin, aligned to the z-axis.

    Exact distance field.
    """
    p = axes()
    df = Vec2(p.xy.length() - major_radius, p.z).length() - minor_radius
    halfwidth = major_radius + minor_radius
    bb = BoundBox(
        -halfwidth, halfwidth, -halfwidth, halfwidth, -minor_radius, minor_radius
    )
    return Shape(df, bb)


def cylinder(radius, height) -> Shape:
    """
    A cylinder, aligned to the z-axis and centered at the origin.

    Exact distance field.
    """
    p = axes()
    d = abs(Vec2(p.xy.length(), p.z)) - Vec2(radius, height)
    df = min_(max_(d.x, d.y), radius * 1e-6) + max_(d, height * 1e-6).length()
    bb = BoundBox(-radius, radius, -radius, radius, -height, height)
    return Shape(df, bb)


def union(a: Shape, b: Shape) -> Shape:
    df = min_(a.tree, b.tree)
    bb = BoundBox(
        min(a.bounds.xmin, b.bounds.xmin),
        max(a.bounds.xmax, b.bounds.xmax),
        min(a.bounds.ymin, b.bounds.ymin),
        max(a.bounds.ymax, b.bounds.ymax),
        min(a.bounds.zmin, b.bounds.zmin),
        max(a.bounds.zmax, b.bounds.zmax),
    )
    return Shape(df, bb)


def intersection(a: Shape, b: Shape) -> Shape:
    df = min_(a.tree, b.tree)
    bb = BoundBox(
        max(a.bounds.xmin, b.bounds.xmin),
        min(a.bounds.xmax, b.bounds.xmax),
        max(a.bounds.ymin, b.bounds.ymin),
        min(a.bounds.ymax, b.bounds.ymax),
        max(a.bounds.zmin, b.bounds.zmin),
        min(a.bounds.zmax, b.bounds.zmax),
    )
    return Shape(df, bb)


def difference(a: Shape, b: Shape) -> Shape:
    df = max_(a.tree, -b.tree)
    bb = a.bounds
    return Shape(df, bb)


def xor(a: Shape, b: Shape) -> Shape:
    df = max_(min_(a.rtee, b.tree), -max_(a.tree, b.tree))
    bb = BoundBox(
        min(a.bounds.xmin, b.bounds.xmin),
        max(a.bounds.xmax, b.bounds.xmax),
        min(a.bounds.ymin, b.bounds.ymin),
        max(a.bounds.ymax, b.bounds.ymax),
        min(a.bounds.zmin, b.bounds.zmin),
        max(a.bounds.zmax, b.bounds.zmax),
    )
    return Shape(df, bb)


def move(shp: Shape, mx, my, mz) -> Shape:
    """
    Translate a shape by the given vector
    """
    mov = Vec3(mx, my, mz)
    return Shape(
        shp.tree.remap_xyz(*(axes() - mov)),
        BoundBox(
            shp.bounds.xmin + mx,
            shp.bounds.xmax + mx,
            shp.bounds.ymin + my,
            shp.bounds.ymax + my,
            shp.bounds.zmin + mz,
            shp.bounds.zmax + mz,
        ),
    )


def expand(shp: Shape, amount: Real) -> Shape:
    """
    Expands a shape by the specified amount.

    For exact distance fields, sharp corners become rounded.
    For mitred distance fields, sharp corners are preserved.
    """
    return Shape(
        shp.tree - amount,
        BoundBox(
            shp.bounds.xmin - amount,
            shp.bounds.xmax + amount,
            shp.bounds.ymin - amount,
            shp.bounds.ymax + amount,
            shp.bounds.zmin - amount,
            shp.bounds.zmax + amount,
        ),
    )


def extrude_z(shp: Shape, height: Real) -> Shape:
    eps = 1e-6 * height
    t = shp.tree
    x, y, z = axes()
    w = Vec2(t, abs(z) - height)
    df = min_(max_(w.x, w.y), eps) + max_(w, eps).length()
    bb = BoundBox(
        shp.bounds.xmin,
        shp.bounds.xmax,
        shp.bounds.ymin,
        shp.bounds.ymax,
        -height,
        height,
    )
    return Shape(df, bb)


def revolve_z(shp: Shape) -> Tree:
    t = shp.tree
    p = axes()
    rotated_up = t.remap_xyz(p.x, p.z, p.y)
    df = rotated_up.remap_xyz(p.xy.length(), p.y, p.z)
    outer_radius = max(abs(shp.bounds.xmin), abs(shp.bounds.xmax))
    bb = BoundBox(
        -1 * outer_radius,
        outer_radius,
        -1 * outer_radius,
        outer_radius,
        shp.bounds.ymin,
        shp.bounds.ymax,
    )
    return Shape(df, bb)
